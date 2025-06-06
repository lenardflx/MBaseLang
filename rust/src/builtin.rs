use crate::base_literal::BaseLiteral;
use std::collections::HashMap;

pub type BuiltinFn = fn(Vec<BaseLiteral>) -> Result<Option<BaseLiteral>, String>;

pub fn builtin_out(args: Vec<BaseLiteral>) -> Result<Option<BaseLiteral>, String> {
    if let Some(arg) = args.get(0) {
        print!("{}", arg);
    }
    Ok(None)
}

pub fn builtin_in(_args: Vec<BaseLiteral>) -> Result<Option<BaseLiteral>, String> {
    use std::io::{self, Write};
    io::stdout().flush().unwrap();
    let mut input = String::new();
    io::stdin().read_line(&mut input).unwrap();
    Ok(Some(BaseLiteral::new(10, input.trim()).unwrap()))
}

pub fn builtin_wait(args: Vec<BaseLiteral>) -> Result<Option<BaseLiteral>, String> {
    if let Some(arg) = args.get(0) {
        std::thread::sleep(std::time::Duration::from_secs(arg.to_int()? as u64));
    }
    Ok(None)
}

pub fn builtins() -> HashMap<&'static str, BuiltinFn> {
    let mut map: HashMap<&'static str, BuiltinFn> = HashMap::new();
    map.insert("out", builtin_out);
    map.insert("in", builtin_in);
    map.insert("wait", builtin_wait);
    map
}
