use crate::token::{Token, TokenType};
use crate::base_literal::VALID_DIGITS;

pub fn tokenize(source: &str) -> Vec<Token> {
    let mut tokens = Vec::new();
    let mut i = 0;
    let chars: Vec<char> = source.chars().collect();
    while i < chars.len() {
        let ch = chars[i];
        if ch == 'b' {
            let mut j = i + 1;
            while j < chars.len() && chars[j].is_ascii_digit() { j += 1; }
            if j < chars.len() && chars[j] == '@' {
                let base: u32 = source[i+1..j].parse().unwrap();
                j += 1;
                let start = j;
                while j < chars.len() && VALID_DIGITS[..base as usize].contains(chars[j]) { j += 1; }
                let raw = &source[start..j];
                tokens.push(Token::new(TokenType::BaseLiteral, Some(format!("{}@{}", base, raw)), i));
                i = j;
                continue;
            }
        }
        if ch == '#' {
            while i < chars.len() && chars[i] != '\n' { i += 1; }
            continue;
        }
        if ch.is_whitespace() {
            if ch == '\n' { tokens.push(Token::new(TokenType::Newline, Some("\n".into()), i)); }
            i += 1;
            continue;
        }
        match ch {
            ';' => { tokens.push(Token::new(TokenType::Semicolon, Some(";".into()), i)); i += 1; }
            ',' => { tokens.push(Token::new(TokenType::Comma, Some(",".into()), i)); i += 1; }
            '{' => { tokens.push(Token::new(TokenType::LBrace, Some("{".into()), i)); i += 1; }
            '}' => { tokens.push(Token::new(TokenType::RBrace, Some("}".into()), i)); i += 1; }
            '(' => { tokens.push(Token::new(TokenType::LParen, Some("(".into()), i)); i += 1; }
            ')' => { tokens.push(Token::new(TokenType::RParen, Some(")".into()), i)); i += 1; }
            '=' => { tokens.push(Token::new(TokenType::Assign, Some("=".into()), i)); i += 1; }
            '+' => { tokens.push(Token::new(TokenType::Plus, Some("+".into()), i)); i += 1; }
            '-' => { tokens.push(Token::new(TokenType::Minus, Some("-".into()), i)); i += 1; }
            '*' => { tokens.push(Token::new(TokenType::Star, Some("*".into()), i)); i += 1; }
            '/' => { tokens.push(Token::new(TokenType::Slash, Some("/".into()), i)); i += 1; }
            '<' => { tokens.push(Token::new(TokenType::LessThan, Some("<".into()), i)); i += 1; }
            '>' => { tokens.push(Token::new(TokenType::GreaterThan, Some(">".into()), i)); i += 1; }
            '!' => { tokens.push(Token::new(TokenType::Not, Some("!".into()), i)); i += 1; }
            '@' => { tokens.push(Token::new(TokenType::At, Some("@".into()), i)); i += 1; }
            '"' => {
                let start = i+1;
                i += 1;
                let mut content = String::new();
                while i < chars.len() && chars[i] != '"' {
                    if chars[i] == '\\' && i + 1 < chars.len() {
                        let esc = chars[i+1];
                        let val = match esc { 'n' => '\n', 't' => '\t', '"' => '"', '\\' => '\\', _ => esc };
                        content.push(val);
                        i += 2;
                    } else {
                        content.push(chars[i]);
                        i += 1;
                    }
                }
                i += 1;
                tokens.push(Token::new(TokenType::Text, Some(content), start-1));
            }
            _ => {
                if ch.is_ascii_digit() {
                    let start = i; while i < chars.len() && chars[i].is_ascii_digit() { i += 1; }
                    tokens.push(Token::new(TokenType::Number, Some(source[start..i].into()), start));
                } else if ch.is_ascii_alphanumeric() || ch == '_' {
                    let start = i; while i < chars.len() && (chars[i].is_ascii_alphanumeric() || chars[i] == '_') { i += 1; }
                    let value = &source[start..i];
                    let ttype = match value {
                        "fn" => TokenType::Function,
                        "ret" => TokenType::Return,
                        "if" => TokenType::If,
                        "else" => TokenType::Else,
                        "while" => TokenType::While,
                        "loop" => TokenType::Loop,
                        "break" => TokenType::Break,
                        "continue" => TokenType::Continue,
                        _ => TokenType::Identifier,
                    };
                    tokens.push(Token::new(ttype, Some(value.into()), start));
                } else {
                    i += 1;
                }
            }
        }
    }
    tokens.push(Token::new(TokenType::Eof, None, source.len()));
    tokens
}
