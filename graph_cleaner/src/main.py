import datetime
import json

from pydgraph import DgraphClient, DgraphClientStub

def get_one_month_ts() -> int:
    today = datetime.date.today()
    last_month = today - datetime.timedelta(days=30)

    epoch = datetime.date(1970,1,1)

    return int((last_month - epoch).total_seconds())


def find_nodes_connected_to(uid):
    query = """
        query n($a: uid)
        {
            n(func: uid($a)) {
                uid,
                dgraph.type
            }
        }
    """


def delete_nodes_older_than(dgraph_client: DgraphClient, oldest_index: int):
    query = """
        query n($a: int)
        {
            n(func: lt(last_index_time, $a)) {
                uid,
                dgraph.type
            }
        }
    """

    variables = {'$a': oldest_index}

    txn = dgraph_client.txn(read_only=False)

    try:
        res = json.loads(
            txn.query(query, variables=variables).json
        )['n']

        for node in res:
            txn.mutate(del_obj={'uid': node['uid']})

        txn.commit()
    finally:
        txn.discard()


def main():
    # Get the time from one month ago as seconds integer
    one_month_ago = get_one_month_ts()

    # Query the graph for last_index_time where last_index_time < one month ago
    dgraph_client = DgraphClient(DgraphClientStub(""))
    delete_nodes_older_than(dgraph_client, one_month_ago)


if __name__ == '__main__':
    main()