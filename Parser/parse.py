from Mbase.error import print_error_with_origin
from Mbase.types import BaseLiteral, Function
from Parser.token_type import TokenType
from Parser.token import Token

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current(self) -> Token:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return Token(TokenType.EOF, None)

    def advance(self):
        self.pos += 1

    def match(self, *types):
        tok = self.current()
        if tok.type in types:
            self.advance()
            return tok
        return None

    def expect(self, ttype):
        tok = self.current()
        if tok.type != ttype:
            raise SyntaxError(f"Expected {ttype}, got {tok.type}")
        self.advance()
        return tok

    def parse(self):
        results = []
        while self.current().type != TokenType.EOF:
            if self.match(TokenType.NEWLINE) or self.match(TokenType.SEMICOLON):
                continue

            if self.current().type == TokenType.FUNCTION:
                stmt = self.parse_function()
            elif self.current().type == TokenType.IF:
                stmt = self.parse_if()
            elif self.current().type in (TokenType.WHILE, TokenType.LOOP):
                stmt = self.parse_while_loop()
            elif self.current().type in (TokenType.BREAK, TokenType.CONTINUE):
                stmt = self.parse_break_continue()
            elif self.current().type == TokenType.IDENTIFIER and self.peek().type == TokenType.ASSIGN:
                stmt = self.parse_statement()
            else:
                stmt = self.parse_expression()
                if self.match(TokenType.SEMICOLON, TokenType.NEWLINE):
                    pass
                elif self.current().type != TokenType.EOF:
                    raise SyntaxError(f"Expected end of expression, got {self.current().type}")

            results.append(stmt)
        return results

    def peek(self):
        if self.pos + 1 < len(self.tokens):
            return self.tokens[self.pos + 1]
        return Token(TokenType.EOF, None)

    def parse_statement(self):
        tok = self.match(TokenType.IDENTIFIER)
        if not tok:
            print_error_with_origin(self.tokens, self.pos, "Expected identifier", label="SyntaxError")
        var_name = tok.value

        self.expect(TokenType.ASSIGN)
        expr = self.parse_expression()

        sep = self.match(TokenType.SEMICOLON, TokenType.NEWLINE)
        if not sep and self.current().type != TokenType.EOF:
            raise SyntaxError(f"Expected end of statement after assignment")
        return "assign", var_name, expr

    def parse_expression(self):
        return self.parse_logical()

    def parse_logical(self):
        expr = self.parse_equality()
        while self.current().type in (TokenType.OR, TokenType.AND):
            op = self.current()
            self.advance()
            right = self.parse_equality()
            expr = ("binop", op.type, expr, right, op.pos)
        return expr

    def parse_equality(self):
        expr = self.parse_comparison()
        while self.current().type in (
                TokenType.EQUAL,
                TokenType.STRICT_EQUAL,
                TokenType.NOTEQUAL,
                TokenType.STRICT_NOTEQUAL
        ):
            op = self.current()
            self.advance()
            right = self.parse_comparison()
            expr = ("binop", op.type, expr, right, op.pos)
        return expr

    def parse_comparison(self):
        expr = self.parse_term()
        while self.current().type in (
                TokenType.LESSTHAN,
                TokenType.LEQ,
                TokenType.GREATERTHAN,
                TokenType.GEQ
        ):
            op = self.current()
            self.advance()
            right = self.parse_term()
            expr = ("binop", op.type, expr, right, op.pos)
        return expr

    def parse_term(self):
        expr = self.parse_factor()
        while self.current().type in (TokenType.PLUS, TokenType.MINUS):
            op = self.current()
            self.advance()
            right = self.parse_factor()
            expr = ("binop", op.type, expr, right, op.pos)
        return expr

    def parse_factor(self):
        expr = self.parse_primary()
        while self.current().type in (TokenType.STAR, TokenType.SLASH):
            op = self.current()
            self.advance()
            right = self.parse_primary()
            expr = ("binop", op.type, expr, right, op.pos)
        return expr

    def parse_primary(self):
        tok = self.current()

        if tok.type == TokenType.RETURN:
            self.advance()
            expr = self.parse_expression()
            return "ret", expr, tok.pos

        elif tok.type == TokenType.NUMBER:
            self.advance()
            return BaseLiteral(10, tok.value)

        elif tok.type == TokenType.IF:
            return self.parse_if()

        elif tok.type == TokenType.WHILE or tok.type == TokenType.LOOP:
            return self.parse_while_loop()

        elif tok.type == TokenType.BREAK or tok.type == TokenType.CONTINUE:
            return self.parse_break_continue()

        elif tok.type == TokenType.BASE_LITERAL:
            self.advance()
            base, value = tok.value
            return BaseLiteral(base, value)

        elif tok.type == TokenType.IDENTIFIER and self.peek().type == TokenType.LPAREN:
            return self.parse_call()

        elif tok.type == TokenType.IDENTIFIER:
            self.advance()
            return "var", tok.value


        elif tok.type == TokenType.TEXT:
            self.advance()
            return "text", tok.value

        elif tok.type == TokenType.LPAREN:
            self.advance()
            expr = self.parse_expression()
            self.expect(TokenType.RPAREN)
            return expr

        display = tok.value if tok.value is not None else tok.type.name
        raise SyntaxError(f"Unexpected token '{display}' in expression")

    def parse_call(self):
        name_tok = self.expect(TokenType.IDENTIFIER)
        self.expect(TokenType.LPAREN)

        args = []
        if self.current().type != TokenType.RPAREN:
            while True:
                args.append(self.parse_expression())
                if self.match(TokenType.COMMA):
                    continue
                break

        self.expect(TokenType.RPAREN)
        return "call", name_tok.value, args, name_tok.pos

    def parse_function(self):
        self.expect(TokenType.FUNCTION)
        name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.LPAREN)

        args = []
        while self.current().type != TokenType.RPAREN:
            typ = self.expect(TokenType.IDENTIFIER).value
            var = self.expect(TokenType.IDENTIFIER).value
            args.append((typ, var))
            if not self.match(TokenType.COMMA):
                break
        self.expect(TokenType.RPAREN)

        return_type = None
        if self.current().type == TokenType.IDENTIFIER and self.peek().type == TokenType.LBRACE:
            return_type = self.expect(TokenType.IDENTIFIER).value

        self.expect(TokenType.LBRACE)
        body = []
        while self.current().type != TokenType.RBRACE:
            if self.match(TokenType.NEWLINE, TokenType.SEMICOLON):
                continue
            if self.current().type == TokenType.IDENTIFIER and self.peek().type == TokenType.ASSIGN:
                body.append(self.parse_statement())
            else:
                body.append(self.parse_expression())

        self.expect(TokenType.RBRACE)

        return Function(name=name, args=args, return_type=return_type, body=body)

    def parse_if(self):
        self.expect(TokenType.IF)
        label = self.parse_optional_label()
        self.expect(TokenType.LPAREN)
        condition = self.parse_expression()
        self.expect(TokenType.RPAREN)
        then_body = self.parse_block()

        else_body = None
        if self.match(TokenType.ELSE):
            if self.current().type == TokenType.IF:
                else_body = [self.parse_if()]
            else:
                else_body = self.parse_block()

        return "if", label, condition, then_body, else_body

    def parse_while_loop(self):
        kind_token = self.current()
        self.advance()
        label = self.parse_optional_label()

        if kind_token.type == TokenType.WHILE:
            self.expect(TokenType.LPAREN)
            condition = self.parse_expression()
            self.expect(TokenType.RPAREN)
            body = self.parse_block()
            return "while", label, condition, body

        elif kind_token.type == TokenType.LOOP:
            body = self.parse_block()
            return "loop", label, body
        return None

    def parse_break_continue(self):
        kind_token = self.current()
        self.advance()
        label = self.parse_optional_label()
        self.match(TokenType.SEMICOLON, TokenType.NEWLINE)

        kind = "break" if kind_token.type == TokenType.BREAK else "continue"
        return kind, label

    def parse_optional_label(self):
        if self.current().type == TokenType.AT:
            self.advance()
            ident = self.expect(TokenType.IDENTIFIER)
            return ident.value
        return None

    def parse_block(self):
        self.expect(TokenType.LBRACE)
        body = []
        while self.current().type != TokenType.RBRACE:
            if self.match(TokenType.NEWLINE, TokenType.SEMICOLON):
                continue
            if self.current().type == TokenType.RETURN:
                self.advance()
                expr = self.parse_expression()
                body.append(("ret", expr, self.pos))
            elif self.current().type == TokenType.IDENTIFIER and self.peek().type == TokenType.ASSIGN:
                body.append(self.parse_statement())
            else:
                body.append(self.parse_expression())
        self.expect(TokenType.RBRACE)
        return body

