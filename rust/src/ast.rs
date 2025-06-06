use crate::token::TokenType;
use crate::base_literal::BaseLiteral;

#[derive(Debug, Clone)]
pub enum Node {
    BaseLiteral(BaseLiteral),
    Var(String),
    Assign { name: String, value: Box<Node> },
    BinOp { op: TokenType, left: Box<Node>, right: Box<Node> },
    Call { name: String, args: Vec<Node> },
    Return(Box<Node>),
    Text(String),
}
