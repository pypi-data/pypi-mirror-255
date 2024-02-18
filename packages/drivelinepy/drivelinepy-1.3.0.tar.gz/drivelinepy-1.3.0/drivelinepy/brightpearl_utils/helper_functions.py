import pandas as pd


def sales_orders_list_to_dataframe(results, columns):
    header_columns = [column["name"] for column in columns]
    return pd.DataFrame(results, columns=header_columns)

def construct_sales_orders_url(ids, base_url):
    string_ids = [str(id) for id in ids]
    return string_ids

def individual_sales_orders_to_dataframe(orders):
    return pd.json_normalize(orders, sep='_')


def append_order_and_individual_sales_entry(orders):
    row_frames = list()
    for _, row in orders.iterrows():
        row_frame = pd.json_normalize(row["rows"])
        # can join later
        row_frame["salesOrderId"] = row["id"]
        row_frame = row_frame.add_prefix("individual_sale_entry_")
        row_frames.append(row_frame)
    row_frames = pd.concat(row_frames)
    megaframe = orders.merge(row_frames, how='right',left_on=["id"], right_on=["individual_sale_entry_salesOrderId"], suffixes=("","sale_entry"))
    megaframe = megaframe.drop("rows",axis=1)
    return megaframe