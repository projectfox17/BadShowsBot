import asyncio
from pprint import pprint

from modules.logger import Logger
from modules.storage import NodeType, NodeSpec, Storage


logger = Logger("Main")


async def main():
    st = Storage("BadShowsBot")
    st.generate_nodes(
        [
            NodeSpec(
                name="aboba", type=NodeType.FILE, relative_path="config/aboba.txt"
            ),
            NodeSpec(
                name="obema", type=NodeType.FILE, relative_path="config/obema.json"
            ),
        ]
    )
    await st.nodes_dump_json(st.root_path / "popa.json")


if __name__ == "__main__":
    asyncio.run(main())
