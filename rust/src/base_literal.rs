#[derive(Debug, Clone, PartialEq, Eq)]
pub struct BaseLiteral {
    pub base: u32,
    pub raw: String,
}

pub const VALID_DIGITS: &str = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ+/";

impl BaseLiteral {
    pub fn new(base: u32, raw: &str) -> Result<Self, String> {
        if base < 2 || base > 64 {
            return Err(format!("Base {} not supported (must be 2-64)", base));
        }
        let raw = raw.to_lowercase();
        let allowed = &VALID_DIGITS[..base as usize];
        for ch in raw.chars() {
            if !allowed.contains(ch) {
                return Err(format!("Digit '{}' not valid in base {}", ch, base));
            }
        }
        Ok(Self { base, raw })
    }

    pub fn to_int(&self) -> Result<u64, String> {
        let digits = &VALID_DIGITS[..self.base as usize];
        let mut val: u64 = 0;
        for ch in self.raw.chars() {
            if let Some(idx) = digits.find(ch) {
                val = val * self.base as u64 + idx as u64;
            } else {
                return Err(format!("Invalid digit '{}' for base {}", ch, self.base));
            }
        }
        Ok(val)
    }

    pub fn from_int(base: u32, mut value: u64) -> Result<Self, String> {
        if value == 0 {
            return Ok(Self { base, raw: "0".to_string() });
        }
        let digits = &VALID_DIGITS[..base as usize];
        let mut result = String::new();
        while value > 0 {
            let idx = (value % base as u64) as usize;
            result.insert(0, digits.chars().nth(idx).unwrap());
            value /= base as u64;
        }
        Ok(Self { base, raw: result })
    }

    fn as_int(&self, other: &BaseLiteral) -> Result<u64, String> {
        other.to_int()
    }

    pub fn add(&self, other: &BaseLiteral) -> Result<Self, String> {
        let result = self.to_int()? + self.as_int(other)?;
        Self::from_int(self.base, result)
    }
    pub fn sub(&self, other: &BaseLiteral) -> Result<Self, String> {
        let result = self.to_int()? - self.as_int(other)?;
        Self::from_int(self.base, result)
    }
    pub fn mul(&self, other: &BaseLiteral) -> Result<Self, String> {
        let result = self.to_int()? * self.as_int(other)?;
        Self::from_int(self.base, result)
    }
    pub fn div(&self, other: &BaseLiteral) -> Result<Self, String> {
        let result = self.to_int()? / self.as_int(other)?;
        Self::from_int(self.base, result)
    }
}

impl std::fmt::Display for BaseLiteral {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        if self.base == 10 {
            write!(f, "{}", self.raw)
        } else {
            write!(f, "b{}@{}", self.base, self.raw)
        }
    }
}
