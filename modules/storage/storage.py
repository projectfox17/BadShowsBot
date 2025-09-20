from pathlib import Path
import aiofiles
import json

from modules.storage import NodeType, NodeSpec, FileNode, DirectoryNode
from modules.storage import StorageException, MissingRequiredNodeError
from modules.logger import Logger


logger = Logger("Storage")


class Storage:

    def __init__(self, root_name: str):
        module_path = Path(__file__)
        root_path = module_path.parents[2].resolve()

        if root_path.name != root_name:
            raise StorageException(
                f"Project root name mismatch: {root_path.name}, expected {root_name}"
            )
        if module_path != root_path / "modules" / "storage" / "storage.py":
            raise StorageException(
                f"Storage module misplacement: {module_path}, "
                f"expected {root_name}/modules/storage/storage.py"
            )

        self._root_path: Path = root_path
        self._nodes: dict[str, FileNode | DirectoryNode] = dict()
        self._missing: dict[str, FileNode | DirectoryNode] = dict()
        self._created: dict[str, FileNode | DirectoryNode] = dict()

    @property
    def root_path(self) -> Path:
        return self._root_path

    @property
    def nodes_list(self) -> list[FileNode | DirectoryNode]:
        return list(self._nodes.values())

    @property
    def missing_nodes(self) -> dict[str, FileNode | DirectoryNode]:
        return self._missing

    @property
    def created_nodes(self) -> dict[str, FileNode | DirectoryNode]:
        return self._created

    def get_node(self, name: str) -> FileNode | DirectoryNode:
        if not self._nodes:
            raise StorageException("Nodes uninitialized, attempted to access")
        return self._nodes[name]

    def generate_nodes(self, node_specs: list[NodeSpec]) -> None:
        """
        Инициализирует фактические ноды FileNode и StorageNode
        на основе скелетов NodeSpec и записывает в Storage.nodes
        """

        fail_nodes: list[str] = []

        for spec in node_specs:

            abs_path = (self.root_path / spec.relative_path).resolve()
            node_str = f"{spec.type.value.capitalize()} {spec.name} at {abs_path}"

            try:

                node = (
                    FileNode(name=spec.name, path=abs_path)
                    if spec.type is NodeType.FILE
                    else DirectoryNode(name=spec.name, path=abs_path)
                )

                if not abs_path.exists():
                    if spec.required:
                        if not spec.missing_ok:
                            logger.critical(
                                f"Required {node_str} missing with no automatic handling"
                            )
                            fail_nodes.append(node_str)
                            continue

                        logger.warning(
                            f"Required {node_str} missing, automated actions are taken further"
                        )
                        self._missing[spec.name] = node

                    # Create missing not required node
                    if spec.type is NodeType.FILE:
                        abs_path.parent.mkdir(parents=True, exist_ok=True)
                        abs_path.touch()
                    elif spec.type is NodeType.DIRECTORY:
                        abs_path.mkdir(parents=True)
                    logger.debug(f"Created {node_str}")
                    self._created[spec.name] = node

                logger.debug(f"Initialized {node_str}")
                self._nodes[spec.name] = node

            except Exception as e:
                logger.critical(f"Failed initializing {node_str}:\n{e}")
                fail_nodes.append(node_str)

        if fail_nodes:
            s = f"Failed initializing nodes:\n{"\n".join(fail_nodes)}"
            logger.critical(s)
            raise StorageException(s)

    async def nodes_load_json(self, path: Path | str) -> None:
        if isinstance(path, str):
            path = Path(path).resolve()

        async with aiofiles.open(path, mode="r") as src:
            d = await src.read()
        j = json.loads(d)
        for node_data in j:
            node = (
                FileNode.model_validate(node_data)
                if node_data["type"] is NodeType.FILE
                else DirectoryNode.model_validate(node_data)
            )
            self._nodes[node.name] = node

    async def nodes_dump_json(self, path: Path | str) -> None:
        if isinstance(path, str):
            path = Path(path).resolve()

        j = json.dumps([n.model_WHAT() for n in self.nodes_list])
        async with aiofiles.open(path, mode="w") as dest:
            await dest.write(j)
