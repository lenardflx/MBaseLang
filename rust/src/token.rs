#[derive(Debug, Clone, PartialEq)]
pub enum TokenType {
    Identifier,
    Number,
    BaseLiteral,
    Text,
    LParen,
    RParen,
    LBrace,
    RBrace,
    Plus,
    Minus,
    Star,
    Slash,
    Assign,
    Equal,
    StrictEqual,
    NotEqual,
    StrictNotEqual,
    LessThan,
    Leq,
    GreaterThan,
    Geq,
    And,
    Or,
    Not,
    If,
    Else,
    While,
    Loop,
    Break,
    Continue,
    Semicolon,
    Comma,
    At,
    Return,
    Function,
    Newline,
    Eof,
}

#[derive(Debug, Clone)]
pub struct Token {
    pub ttype: TokenType,
    pub value: Option<String>,
    pub pos: usize,
}

impl Token {
    pub fn new(ttype: TokenType, value: Option<String>, pos: usize) -> Self {
        Self { ttype, value, pos }
    }
}
