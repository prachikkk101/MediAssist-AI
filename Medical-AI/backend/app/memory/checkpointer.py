from langgraph.checkpoint.sqlite import SqliteSaver


def get_checkpointer():

    checkpointer = SqliteSaver.from_conn_string(
        "memory.db"
    )

    return checkpointer