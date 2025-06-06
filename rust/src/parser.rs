use crate::token::{Token, TokenType};
use crate::ast::Node;
use crate::base_literal::BaseLiteral;

pub struct Parser {
    tokens: Vec<Token>,
    pos: usize,
}

impl Parser {
    pub fn new(tokens: Vec<Token>) -> Self {
        Self { tokens, pos: 0 }
    }

    fn current(&self) -> &Token {
        &self.tokens[self.pos]
    }

    fn advance(&mut self) { self.pos += 1; }

    fn match_type(&mut self, ttypes: &[TokenType]) -> Option<Token> {
        if self.pos < self.tokens.len() {
            let tok = self.current();
            if ttypes.contains(&tok.ttype) {
                let tok = tok.clone();
                self.advance();
                return Some(tok);
            }
        }
        None
    }

    fn expect(&mut self, ttype: TokenType) -> Token {
        let tok = self.current();
        if tok.ttype != ttype {
            panic!("expected {:?}, got {:?}", ttype, tok.ttype);
        }
        let tok = tok.clone();
        self.advance();
        tok
    }

    pub fn parse(&mut self) -> Vec<Node> {
        let mut results = Vec::new();
        while self.current().ttype != TokenType::Eof {
            if self.match_type(&[TokenType::Newline, TokenType::Semicolon]).is_some() {
                continue;
            }
            if let Some(id) = self.match_type(&[TokenType::Identifier]) {
                if self.current().ttype == TokenType::Assign {
                    self.advance();
                    let expr = self.parse_expression();
                    results.push(Node::Assign { name: id.value.unwrap(), value: Box::new(expr) });
                    self.match_type(&[TokenType::Semicolon, TokenType::Newline]);
                    continue;
                } else {
                    self.pos -= 1;
                }
            }
            let expr = self.parse_expression();
            self.match_type(&[TokenType::Semicolon, TokenType::Newline]);
            results.push(expr);
        }
        results
    }

    fn parse_expression(&mut self) -> Node {
        self.parse_term()
    }

    fn parse_term(&mut self) -> Node {
        let mut node = self.parse_factor();
        while let Some(op_tok) = self.match_type(&[TokenType::Plus, TokenType::Minus]) {
            let right = self.parse_factor();
            node = Node::BinOp { op: op_tok.ttype, left: Box::new(node), right: Box::new(right) };
        }
        node
    }

    fn parse_factor(&mut self) -> Node {
        let mut node = self.parse_primary();
        while let Some(op_tok) = self.match_type(&[TokenType::Star, TokenType::Slash]) {
            let right = self.parse_primary();
            node = Node::BinOp { op: op_tok.ttype, left: Box::new(node), right: Box::new(right) };
        }
        node
    }

    fn parse_primary(&mut self) -> Node {
        let tok = self.current().clone();
        match tok.ttype {
            TokenType::Number => {
                self.advance();
                Node::BaseLiteral(BaseLiteral::new(10, tok.value.as_ref().unwrap()).unwrap())
            }
            TokenType::BaseLiteral => {
                self.advance();
                let parts: Vec<&str> = tok.value.as_ref().unwrap().split('@').collect();
                let base: u32 = parts[0].parse().unwrap();
                let raw = parts[1];
                Node::BaseLiteral(BaseLiteral::new(base, raw).unwrap())
            }
            TokenType::Identifier => {
                self.advance();
                if self.current().ttype == TokenType::LParen {
                    self.advance();
                    let mut args = Vec::new();
                    if self.current().ttype != TokenType::RParen {
                        loop {
                            let expr = self.parse_expression();
                            args.push(expr);
                            if self.match_type(&[TokenType::Comma]).is_some() { continue; }
                            break;
                        }
                    }
                    self.expect(TokenType::RParen);
                    Node::Call { name: tok.value.unwrap(), args }
                } else {
                    Node::Var(tok.value.unwrap())
                }
            }
            TokenType::LParen => {
                self.advance();
                let expr = self.parse_expression();
                self.expect(TokenType::RParen);
                expr
            }
            TokenType::Text => {
                self.advance();
                Node::Text(tok.value.unwrap())
            }
            _ => panic!("unexpected token {:?}", tok.ttype),
        }
    }
}
