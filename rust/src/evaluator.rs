use crate::ast::Node;
use crate::builtin::builtins;
use crate::base_literal::BaseLiteral;
use crate::token::TokenType;
use std::collections::HashMap;

pub fn evaluate(nodes: &[Node]) {
    let mut ctx: HashMap<String, BaseLiteral> = HashMap::new();
    let builtins = builtins();
    for node in nodes {
        eval_node(node, &mut ctx, &builtins);
    }
}

fn eval_node(node: &Node, ctx: &mut HashMap<String, BaseLiteral>, builtins: &HashMap<&str, crate::builtin::BuiltinFn>) -> Option<BaseLiteral> {
    match node {
        Node::BaseLiteral(b) => Some(b.clone()),
        Node::Var(name) => ctx.get(name).cloned(),
        Node::Assign { name, value } => {
            if let Some(val) = eval_node(value, ctx, builtins) {
                ctx.insert(name.clone(), val);
            }
            None
        }
        Node::BinOp { op, left, right } => {
            let l = eval_node(left, ctx, builtins).unwrap();
            let r = eval_node(right, ctx, builtins).unwrap();
            match op {
                TokenType::Plus => Some(l.add(&r).unwrap()),
                TokenType::Minus => Some(l.sub(&r).unwrap()),
                TokenType::Star => Some(l.mul(&r).unwrap()),
                TokenType::Slash => Some(l.div(&r).unwrap()),
                _ => None,
            }
        }
        Node::Call { name, args } => {
            if let Some(func) = builtins.get(name.as_str()) {
                let mut vals = Vec::new();
                for a in args { if let Some(v) = eval_node(a, ctx, builtins) { vals.push(v); } }
                func(vals).unwrap_or(None)
            } else { None }
        }
        Node::Return(expr) => eval_node(expr, ctx, builtins),
        Node::Text(t) => { print!("{}", t); None }
    }
}
