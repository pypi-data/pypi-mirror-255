import unittest

from packages import transform_utils as tu

class TestTranslateSql(unittest.TestCase):

    def test_simple_snowflake_sql(self):
        sql = "SELECT * FROM XX-XX.YYY.my_table"
        input_ids = ['my_table']

        result = tu.translate_sql("snowflake-sql", sql=sql, input_ids=input_ids)

        expected_sql = "SELECT * FROM {{my_table}}"
        self.assertEqual(result, expected_sql)

    def test_more_complex_snowflake_sql(self):
        sql = "SELECT * FROM XX-XX.YYY.table1, XX-XX.YYY.table2"
        input_ids = ['table2', 'table1']

        result = tu.translate_sql("snowflake-sql", sql=sql, input_ids=input_ids)

        expected_sql = "SELECT * FROM {{table1}}, {{table2}}"
        self.assertEqual(result, expected_sql)

    def test_simple_bigquery_sql(self):
        sql = "SELECT * FROM XX-XX.YYY.my_table"
        input_ids = ['my_table']

        result = tu.translate_sql("bigquery-sql", sql=sql, input_ids=input_ids)

        expected_sql = "SELECT * FROM {{my_table}}"
        self.assertEqual(result, expected_sql)

    def test_quoted_bigquery_sql(self):
        sql = "SELECT * FROM `XX-XX`.`YYY`.`my_table`"
        input_ids = ['my_table']

        result = tu.translate_sql("bigquery-sql", sql=sql, input_ids=input_ids)

        expected_sql = "SELECT * FROM {{my_table}}"
        self.assertEqual(result, expected_sql)

    def test_simple_databricks_sql(self):
        sql = "SELECT * FROM `XXX`.`YYY`.`my_table`"
        input_ids = ['my_table']

        result = tu.translate_sql("databricks-sql", sql=sql, input_ids=input_ids)

        expected_sql = "SELECT * FROM {{my_table}}"
        self.assertEqual(result, expected_sql)

    def test_wrong_databricks_sql(self):
        sql = "SELECT * FROM `XXX`.`YYY`.`ZZZ`"
        input_ids = ['my_table']

        result = tu.translate_sql("databricks-sql", sql=sql, input_ids=input_ids)

        self.assertEqual(result, sql)

    def test_wrong_bq_sql(self):
        sql = "SELECT * FROM XXX.YYY.ZZZ"
        input_ids = ['my_table']

        result = tu.translate_sql("bigquery-sql", sql=sql, input_ids=input_ids)

        self.assertEqual(result, sql)

    def test_mesh_snowflake_sql_1(self):

        self.maxDiff = None

        sql = """
                with

                customers as (

                    select * from ASCEND__MHYATT_SF_DEMO.None.stg_customers

                ),

                orders_table as (

                    select * from ASCEND__MHYATT_SF_DEMO.None.orders

                ),

                order_items_table as (

                    select * from ASCEND__MHYATT_SF_DEMO.None.order_items
                ),

                order_summary as (

                    select
                        orders.customer_id,

                        count(distinct orders.order_id) as count_lifetime_orders,
                        count(distinct orders.order_id) > 1 as is_repeat_buyer,
                        min(orders.ordered_at) as first_ordered_at,
                        max(orders.ordered_at) as last_ordered_at,
                        sum(order_items.product_price) as lifetime_spend_pretax,
                        sum(orders.order_total) as lifetime_spend

                    from orders_table as orders

                    left join
                        order_items_table as order_items
                        on orders.order_id = order_items.order_id

                    group by 1

                ),

                joined as (

                    select
                        customers.*,
                        order_summary.count_lifetime_orders,
                        order_summary.first_ordered_at,
                        order_summary.last_ordered_at,
                        order_summary.lifetime_spend_pretax,
                        order_summary.lifetime_spend,

                        case
                            when order_summary.is_repeat_buyer then 'returning'
                            else 'new'
                        end as customer_type

                    from customers

                    left join order_summary
                        on customers.customer_id = order_summary.customer_id

                )
        """.strip()
        sql_out = """
                with

                customers as (

                    select * from {{stg_customers}}

                ),

                orders_table as (

                    select * from {{orders}}

                ),

                order_items_table as (

                    select * from {{order_items}}
                ),

                order_summary as (

                    select
                        orders.customer_id,

                        count(distinct orders.order_id) as count_lifetime_orders,
                        count(distinct orders.order_id) > 1 as is_repeat_buyer,
                        min(orders.ordered_at) as first_ordered_at,
                        max(orders.ordered_at) as last_ordered_at,
                        sum(order_items.product_price) as lifetime_spend_pretax,
                        sum(orders.order_total) as lifetime_spend

                    from orders_table as orders

                    left join
                        order_items_table as order_items
                        on orders.order_id = order_items.order_id

                    group by 1

                ),

                joined as (

                    select
                        customers.*,
                        order_summary.count_lifetime_orders,
                        order_summary.first_ordered_at,
                        order_summary.last_ordered_at,
                        order_summary.lifetime_spend_pretax,
                        order_summary.lifetime_spend,

                        case
                            when order_summary.is_repeat_buyer then 'returning'
                            else 'new'
                        end as customer_type

                    from customers

                    left join order_summary
                        on customers.customer_id = order_summary.customer_id

                )
        """.strip()

        input_ids = ['stg_customers', 'orders', 'order_items']

        result = tu.translate_sql("snowflake-sql", sql=sql, input_ids=input_ids)

        self.assertEqual(result, sql_out)        

    def test_mesh_snowflake_sql_2(self):

        self.maxDiff = None

        sql = """
                with

                orders as (

                    select * from ASCEND__MHYATT_SF_DEMO.None.stg_orders

                ),

                order_items_table as (

                    select * from ASCEND__MHYATT_SF_DEMO.PUBLIC.order_items

                ),

                order_items_summary as (

                    select

                        order_id,
                        count(case when is_food_item then 1 else 0 end)
                            as count_food_items,
                        count(case when is_drink_item then 1 else 0 end)
                            as count_drink_items,

                        sum(supply_cost) as order_cost

                    from order_items_table

                    group by 1

                ),


                compute_booleans as (
                    select

                        orders.*,
                        order_items_summary.order_cost,
                        order_items_summary.count_food_items > 0 as is_food_order,
                        order_items_summary.count_drink_items > 0 as is_drink_order

                    from orders

                    left join
                        order_items_summary
                        on orders.order_id = order_items_summary.order_id
                )

                select * from compute_booleans
        """.strip()
        sql_out = """
                with

                orders as (

                    select * from {{stg_orders}}

                ),

                order_items_table as (

                    select * from {{order_items}}

                ),

                order_items_summary as (

                    select

                        order_id,
                        count(case when is_food_item then 1 else 0 end)
                            as count_food_items,
                        count(case when is_drink_item then 1 else 0 end)
                            as count_drink_items,

                        sum(supply_cost) as order_cost

                    from order_items_table

                    group by 1

                ),


                compute_booleans as (
                    select

                        orders.*,
                        order_items_summary.order_cost,
                        order_items_summary.count_food_items > 0 as is_food_order,
                        order_items_summary.count_drink_items > 0 as is_drink_order

                    from orders

                    left join
                        order_items_summary
                        on orders.order_id = order_items_summary.order_id
                )

                select * from compute_booleans
        """.strip()

        input_ids = ['stg_orders', 'order_items']

        result = tu.translate_sql("snowflake-sql", sql=sql, input_ids=input_ids)

        self.assertEqual(result, sql_out)   
     