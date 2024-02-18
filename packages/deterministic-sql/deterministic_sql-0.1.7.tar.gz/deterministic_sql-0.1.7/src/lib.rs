use core::ops::ControlFlow;
use sqlparser::ast::*;
use sqlparser::dialect::AnsiDialect;
use sqlparser::parser::Parser;
use std::iter::zip;

use pyo3::prelude::*;

const DATE_COLUMN_NAMES: [&'static str; 3] = ["date", "p_date", "pdate"];
const ARRAY_AGG_FUNCS: [&'static str; 5] = [
    "array_agg",
    "set_agg",
    "collect_set",
    "collect_list",
    "array_set",
];
const ARRAY_SORT: &'static str = "array_sort";
const FUNCTIONS_FOR_REPLACE: [&'static str; 8] = [
    "approx_set",
    "rand",
    "random",
    "bytedance_rand",
    "now",
    "approx_distinct",
    "aeolus_approx_distinct",
    "unix_timestamp",
];
fn replace_function_name(expr: &mut Expr, name: String) {
    match expr {
        Expr::Function(function) => function.name.0[0].value = name,
        _ => (),
    }
}
fn replace_approx_percentile(expr: &mut Expr) {
    replace_function_name(expr, "percentile".to_owned())
}
fn replace_approx_set(expr: &mut Expr) {
    replace_function_name(expr, "set_agg".to_owned())
}
fn replace_rand(expr: &mut Expr) {
    *expr = Expr::Value(Value::Number(String::from("0"), false))
}
fn replace_now(expr: &mut Expr) {
    *expr = Expr::Cast {
        expr: Expr::Value(Value::SingleQuotedString("2024-01-29 14:25:43".to_owned())).into(),
        data_type: DataType::Timestamp(Option::None, TimezoneInfo::WithTimeZone),
        format: Option::None,
    }
}
fn replace_approx_distinct(expr: &mut Expr) {
    match expr {
        Expr::Function(function) => {
            function.name.0[0].value = "count".to_owned();
            function.distinct = true;
        }
        _ => (),
    }
}
fn replace_unix_timestamp(expr: &mut Expr) {
    match expr {
        Expr::Function(function) => {
            if !function.args.is_empty() {
                return;
            }
        }
        _ => (),
    }
    *expr = Expr::Value(Value::Number(String::from("1706514942"), false))
}
const REPLACE_IMPLS: [fn(&mut Expr); 8] = [
    replace_approx_set,
    replace_rand,
    replace_rand,
    replace_rand,
    replace_now,
    replace_approx_distinct,
    replace_approx_distinct,
    replace_unix_timestamp,
];

struct Formalizer {
    is_outermost: bool,
    output_columns: usize,
}

impl Formalizer {
    pub fn new(output_columns: usize) -> Self {
        let is_outermost = true;
        Self {
            is_outermost,
            output_columns,
        }
    }

    fn pre_visit_outermost_query(&mut self, query: &mut Query) {
        let body = query.body.as_ref();
        match body {
            SetExpr::Select(select) => {
                if self.output_columns == 0 {
                    query.order_by = construct_order_by(select.projection.len());
                } else {
                    query.order_by = construct_order_by(self.output_columns);
                }
                if need_to_add_limit(&query.limit) {
                    query.limit = Some(Expr::Value(Value::Number(String::from("20000"), false)));
                }
                query.limit_by = vec![];
            }
            SetExpr::SetOperation {
                left,
                op: _,
                set_quantifier: _,
                right: _,
            } => match left.as_ref() {
                SetExpr::Select(select) => {
                    if self.output_columns == 0 {
                        query.order_by = construct_order_by(select.projection.len());
                    } else {
                        query.order_by = construct_order_by(self.output_columns);
                    }
                    if need_to_add_limit(&query.limit) {
                        query.limit =
                            Some(Expr::Value(Value::Number(String::from("20000"), false)));
                    }
                }
                _ => (),
            },
            _ => (),
        }
    }

    pub fn pre_visit_inner_query(&mut self, query: &mut Query) {
        if query.limit.is_none() {
            return;
        }
        let body = query.body.as_ref();
        match body {
            SetExpr::Select(select) => {
                query.order_by = construct_order_by(select.projection.len());
                if need_to_add_limit(&query.limit) {
                    query.limit = Some(Expr::Value(Value::Number(String::from("20000"), false)));
                }
                query.limit_by = vec![];
            }
            SetExpr::SetOperation {
                left,
                op: _,
                set_quantifier: _,
                right: _,
            } => match left.as_ref() {
                SetExpr::Select(select) => {
                    query.order_by = construct_order_by(select.projection.len());
                    if need_to_add_limit(&query.limit) {
                        query.limit =
                            Some(Expr::Value(Value::Number(String::from("20000"), false)));
                    }
                    query.limit_by = vec![];
                }
                _ => (),
            },
            _ => (),
        }
    }
}

fn construct_order_by(count: usize) -> Vec<OrderByExpr> {
    let mut v = Vec::new();
    for i in 1..count + 1 {
        let number = Value::Number(i.to_string(), false);
        let expr = Expr::Value(number);
        v.push(OrderByExpr {
            expr,
            asc: None,
            nulls_first: None,
        });
    }
    v
}

fn need_to_add_limit(limit: &Option<Expr>) -> bool {
    match limit {
        Some(limit) => match limit {
            Expr::Value(value) => match value {
                Value::Number(val, _) => {
                    let parsed: Result<u32, _> = val.parse();
                    match &parsed {
                        Ok(val) => {
                            if val <= &20000 {
                                false
                            } else {
                                true
                            }
                        }
                        Err(_) => true,
                    }
                }
                _ => true,
            },
            _ => true,
        },
        _ => true,
    }
}

fn formalize_array_agg(func: &mut Function) -> bool {
    if func.name.0.len() != 1 || func.args.len() != 1 {
        return false;
    }
    let mut name_matched = false;
    ARRAY_AGG_FUNCS.into_iter().for_each(|array_agg_func| {
        if func.name.0[0].value.to_ascii_lowercase() == array_agg_func {
            name_matched = true;
        }
    });
    if !name_matched {
        return false;
    }

    func.args[0] = FunctionArg::Unnamed(FunctionArgExpr::Expr(Expr::Function(func.clone())));
    func.name.0[0].value.clear();
    func.name.0[0].value.push_str(ARRAY_SORT);
    true
}

fn formalize_binop(left: &Box<Expr>, op: &mut BinaryOperator, right: &Box<Expr>) {
    match op {
        BinaryOperator::Gt => (),
        BinaryOperator::GtEq => (),
        BinaryOperator::Lt => (),
        BinaryOperator::LtEq => (),
        _ => return,
    }
    match left.as_ref() {
        Expr::Identifier(ident) => {
            let mut name_matched = false;
            DATE_COLUMN_NAMES.into_iter().for_each(|s| {
                if s == ident.value {
                    name_matched = true;
                }
            });
            if !name_matched {
                return;
            }
            match op {
                BinaryOperator::Gt => *op = BinaryOperator::Eq,
                BinaryOperator::GtEq => *op = BinaryOperator::Eq,
                _ => (),
            }
            return;
        }
        _ => (),
    }
    match right.as_ref() {
        Expr::Identifier(ident) => {
            let mut name_matched = false;
            DATE_COLUMN_NAMES.into_iter().for_each(|s| {
                if s == ident.value {
                    name_matched = true;
                }
            });
            if !name_matched {
                return;
            }
            match op {
                BinaryOperator::Lt => *op = BinaryOperator::Eq,
                BinaryOperator::LtEq => *op = BinaryOperator::Eq,
                _ => (),
            }
        }
        _ => (),
    }
}

impl VisitorMut for Formalizer {
    type Break = ();

    fn pre_visit_query(&mut self, query: &mut Query) -> ControlFlow<Self::Break> {
        if self.is_outermost {
            self.pre_visit_outermost_query(query);
            self.is_outermost = false;
            ControlFlow::Continue(())
        } else {
            self.pre_visit_inner_query(query);
            ControlFlow::Continue(())
        }
    }

    fn post_visit_expr(&mut self, _expr: &mut Expr) -> ControlFlow<Self::Break> {
        match _expr {
            Expr::BinaryOp { left, op, right } => formalize_binop(left, op, right),
            Expr::Function(function) => {
                if formalize_array_agg(function) {
                    ()
                } else {
                    if function.name.0.len() != 1 {
                        return ControlFlow::Continue(());
                    }
                    for (function_name, replace_impl) in zip(FUNCTIONS_FOR_REPLACE, REPLACE_IMPLS) {
                        if function.name.0[0].value.to_ascii_lowercase() == function_name {
                            return (|| {
                                replace_impl(_expr);
                                ControlFlow::Continue(())
                            })();
                        }
                    }
                    return ControlFlow::Continue(());
                }
            }
            _ => (),
        };
        ControlFlow::Continue(())
    }
}

fn make_deterministic(sql: &str, output_columns: usize) -> String {
    let result = Parser::parse_sql(&AnsiDialect {}, sql);
    match result {
        Ok(mut statements) => {
            if statements.len() == 0 {
                "".to_owned()
            } else {
                let mut first_statement = &mut statements[0];
                make_deterministic_impl(&mut first_statement, output_columns)
            }
        }
        Err(_) => "".to_owned(),
    }
}

fn make_deterministic_impl(statement: &mut Statement, output_columns: usize) -> String {
    let mut visitor = Formalizer::new(output_columns);
    statement.visit(&mut visitor);
    statement.to_string()
}

struct FindNthExpr {
    n: usize,
    expr: String,
}

impl Visitor for FindNthExpr {
    type Break = ();

    fn pre_visit_query(&mut self, _query: &Query) -> ControlFlow<Self::Break> {
        match _query.body.as_ref() {
            SetExpr::Select(select) => {
                if self.n < select.projection.len() {
                    match &select.projection[self.n] {
                        SelectItem::UnnamedExpr(expr) => {
                            self.expr = expr.to_string();
                        }
                        SelectItem::ExprWithAlias { expr, alias: _ } => {
                            self.expr = expr.to_string();
                        }
                        SelectItem::QualifiedWildcard(_, _) => (),
                        SelectItem::Wildcard(_) => (),
                    }
                }
            }
            SetExpr::SetOperation {
                left,
                op: _,
                set_quantifier: _,
                right: _,
            } => match left.as_ref() {
                SetExpr::Select(select) => {
                    if self.n < select.projection.len() {
                        match &select.projection[self.n] {
                            SelectItem::UnnamedExpr(expr) => {
                                self.expr = expr.to_string();
                            }
                            SelectItem::ExprWithAlias { expr, alias: _ } => {
                                self.expr = expr.to_string();
                            }
                            SelectItem::QualifiedWildcard(_, _) => (),
                            SelectItem::Wildcard(_) => (),
                        }
                    }
                }
                _ => (),
            },
            _ => (),
        }

        ControlFlow::Break(())
    }
}

fn find_nth_expr(sql: &str, n: usize) -> String {
    let mut visitor = FindNthExpr { n, expr: "".into() };
    let result = Parser::parse_sql(&AnsiDialect {}, sql);
    match result {
        Ok(ast) => {
            ast.visit(&mut visitor);
            visitor.expr
        }
        Err(_) => "".into(),
    }
}

#[pyfunction]
#[pyo3(text_signature = "(sql, n)")]
#[pyo3(name = "find_nth_expr")]
fn find_nth_expr_python_wrapper(sql: &str, n: usize) -> PyResult<String> {
    Ok(find_nth_expr(sql, n))
}

#[pyfunction]
#[pyo3(text_signature = "(sql, output_columns)")]
#[pyo3(name = "make_deterministic")]
fn make_deterministic_python_wrapper(sql: &str, output_columns: usize) -> PyResult<String> {
    Ok(make_deterministic(sql, output_columns))
}

#[pymodule]
fn deterministic_sql(_py: Python<'_>, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(make_deterministic_python_wrapper, m)?)?;
    m.add_function(wrap_pyfunction!(find_nth_expr_python_wrapper, m)?)?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use crate::find_nth_expr;
    use crate::make_deterministic;

    #[test]
    fn simple() {
        let sql = "select a, b, c from t";
        assert_eq!(
            make_deterministic(sql, 3),
            "SELECT a, b, c FROM t ORDER BY 1, 2, 3 LIMIT 20000"
        );
    }

    #[test]
    fn nested() {
        let sql = "select a, b, c from (select a, b, c from t)";
        assert_eq!(
            make_deterministic(sql, 3),
            "SELECT a, b, c FROM (SELECT a, b, c FROM t) ORDER BY 1, 2, 3 LIMIT 20000"
        );

        let sql = "select a, b, c from (select a, b, c from t limit 10)";
        assert_eq!(
            make_deterministic(sql, 3),
            "SELECT a, b, c FROM (SELECT a, b, c FROM t ORDER BY 1, 2, 3 LIMIT 10) ORDER BY 1, 2, 3 LIMIT 20000"
        );

        let sql = "select a, b, c from (select a, b, c from t limit 100000)";
        assert_eq!(
            make_deterministic(sql, 3),
            "SELECT a, b, c FROM (SELECT a, b, c FROM t ORDER BY 1, 2, 3 LIMIT 20000) ORDER BY 1, 2, 3 LIMIT 20000"
        );
    }

    #[test]
    fn limit() {
        let sql = "select a, b, c from t limit 10";
        assert_eq!(
            make_deterministic(sql, 3),
            "SELECT a, b, c FROM t ORDER BY 1, 2, 3 LIMIT 10"
        );
    }

    #[test]
    fn wild() {
        let sql = "select * from t limit 10";
        assert_eq!(
            make_deterministic(sql, 1),
            "SELECT * FROM t ORDER BY 1 LIMIT 10"
        );
    }

    #[test]
    fn union() {
        let sql = "select a from t1 union all select b from t2";
        assert_eq!(
            make_deterministic(sql, 1),
            "SELECT a FROM t1 UNION ALL SELECT b FROM t2 ORDER BY 1 LIMIT 20000"
        );
        assert_eq!(
            make_deterministic(sql, 0),
            "SELECT a FROM t1 UNION ALL SELECT b FROM t2 ORDER BY 1 LIMIT 20000"
        );
    }

    #[test]
    fn join() {
        let sql = "
            SELECT orders.order_id, orders.order_amount, customers.customer_name
            FROM orders
            INNER JOIN ( SELECT customer_id, customer_name
                FROM customers
            ) AS customers ON orders.customer_id = customers.customer_id;";
        assert_eq!(
            make_deterministic(sql, 3),
            "SELECT orders.order_id, orders.order_amount, customers.customer_name FROM orders JOIN (SELECT customer_id, customer_name FROM customers) AS customers ON orders.customer_id = customers.customer_id ORDER BY 1, 2, 3 LIMIT 20000"
        );
    }

    #[test]
    fn formalize_partition() {
        let sql = "SELECT a FROM t WHERE date >= '20240101'";
        assert_eq!(
            make_deterministic(sql, 1),
            "SELECT a FROM t WHERE date = '20240101' ORDER BY 1 LIMIT 20000"
        );
        let sql = "SELECT a FROM t WHERE date > '20240101'";
        assert_eq!(
            make_deterministic(sql, 1),
            "SELECT a FROM t WHERE date = '20240101' ORDER BY 1 LIMIT 20000"
        );
        let sql = "SELECT a FROM t WHERE '20240101' <= date";
        assert_eq!(
            make_deterministic(sql, 1),
            "SELECT a FROM t WHERE '20240101' = date ORDER BY 1 LIMIT 20000"
        );
        let sql = "SELECT a FROM t WHERE '20240101' < date";
        assert_eq!(
            make_deterministic(sql, 1),
            "SELECT a FROM t WHERE '20240101' = date ORDER BY 1 LIMIT 20000"
        );
        let sql = "SELECT a FROM t WHERE name = 'Tom' AND date >= '20240101'";
        assert_eq!(
            make_deterministic(sql, 1),
            "SELECT a FROM t WHERE name = 'Tom' AND date = '20240101' ORDER BY 1 LIMIT 20000"
        );
    }

    #[test]
    fn array_sort() {
        let sql = "SELECT set_agg(a) FROM t";
        assert_eq!(
            make_deterministic(sql, 1),
            "SELECT array_sort(set_agg(a)) FROM t ORDER BY 1 LIMIT 20000"
        );
    }

    #[test]
    fn replace_function() {
        let sql = "SELECT approx_percentile(val) FROM t";
        assert_eq!(
            make_deterministic(sql, 0),
            "SELECT percentile(val) FROM t ORDER BY 1 LIMIT 20000"
        );

        let sql = "SELECT PERCENTILE_APPROX(val) FROM t";
        assert_eq!(
            make_deterministic(sql, 0),
            "SELECT percentile(val) FROM t ORDER BY 1 LIMIT 20000"
        );

        let sql = "SELECT now()";
        assert_eq!(
            make_deterministic(sql, 0),
            "SELECT CAST('2024-01-29 14:25:43' AS TIMESTAMP WITH TIME ZONE) ORDER BY 1 LIMIT 20000"
        );

        let sql = "SELECT approx_distinct(val) FROM t";
        assert_eq!(
            make_deterministic(sql, 0),
            "SELECT count(DISTINCT val) FROM t ORDER BY 1 LIMIT 20000"
        );

        let sql = "SELECT rand(), rand(val) FROM t";
        assert_eq!(
            make_deterministic(sql, 0),
            "SELECT 0, 0 FROM t ORDER BY 1, 2 LIMIT 20000"
        );

        let sql = "SELECT unix_timestamp(), unix_timestamp(val) FROM t";
        assert_eq!(
            make_deterministic(sql, 0),
            "SELECT 1706514942, unix_timestamp(val) FROM t ORDER BY 1, 2 LIMIT 20000"
        );
    }

    #[test]
    fn test_find_nth_expr() {
        let sql = r#"
        SELECT
        "category_one" AS "_1700034018660",
        "category_three" AS "_1700034018662",
        SUM("impression_cnt") AS "_sum_1700020021300",
        SUM("client_impression_cnt") AS "_sum_1700020021301",
        SUM("read_cnt") AS "_sum_1700020021302",
        CAST(SUM("read_cnt") AS DOUBLE) / CAST(SUM("client_impression_cnt") AS DOUBLE) AS "_1700034429208",
        SUM("stay_duration") AS "_sum_1700020021306"
        "#;
        assert_eq!(find_nth_expr(sql, 0), r#""category_one""#);
        assert_eq!(
            find_nth_expr(sql, 5),
            r#"CAST(SUM("read_cnt") AS DOUBLE) / CAST(SUM("client_impression_cnt") AS DOUBLE)"#
        );
        let sql = r#"
        SELECT
        "category_one" AS "_1700034018660",
        "category_three" AS "_1700034018662",
        SUM("impression_cnt") AS "_sum_1700020021300",
        SUM("client_impression_cnt") AS "_sum_1700020021301",
        SUM("read_cnt") AS "_sum_1700020021302",
        CAST(SUM("read_cnt") AS DOUBLE) / CAST(SUM("client_impression_cnt") AS DOUBLE) AS "_1700034429208",
        SUM("stay_duration") AS "_sum_1700020021306"
        UNION
        SELECT
        "category_one" AS "_1700034018660",
        "category_three" AS "_1700034018662",
        SUM("impression_cnt") AS "_sum_1700020021300",
        SUM("client_impression_cnt") AS "_sum_1700020021301",
        SUM("read_cnt") AS "_sum_1700020021302",
        CAST(SUM("read_cnt") AS DOUBLE) / CAST(SUM("client_impression_cnt") AS DOUBLE) AS "_1700034429208",
        SUM("stay_duration") AS "_sum_1700020021306"
        "#;
        assert_eq!(find_nth_expr(sql, 0), r#""category_one""#);
        assert_eq!(
            find_nth_expr(sql, 5),
            r#"CAST(SUM("read_cnt") AS DOUBLE) / CAST(SUM("client_impression_cnt") AS DOUBLE)"#
        );
    }
}
