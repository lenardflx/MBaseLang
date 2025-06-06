mod base_literal;
mod token;
mod tokenizer;
mod parser;
mod ast;
mod evaluator;
mod builtin;

use std::fs;

fn main() {
    let args: Vec<String> = std::env::args().collect();
    if args.len() < 2 {
        eprintln!("Usage: {} <file>", args[0]);
        std::process::exit(1);
    }
    let source = fs::read_to_string(&args[1]).expect("Failed to read file");
    let tokens = tokenizer::tokenize(&source);
    let mut parser = parser::Parser::new(tokens);
    let nodes = parser.parse();
    evaluator::evaluate(&nodes);
}
