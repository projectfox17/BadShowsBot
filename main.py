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
                name="alpha", type=NodeType.FILE, relative_path="config/alpha.txt"
            ),
            NodeSpec(name="beta", type=NodeType.FILE, relative_path="config/beta.json"),
        ]
    )
    await st.nodes_dump_json(st.root_path / "dump.json")


if __name__ == "__main__":
    asyncio.run(main())
