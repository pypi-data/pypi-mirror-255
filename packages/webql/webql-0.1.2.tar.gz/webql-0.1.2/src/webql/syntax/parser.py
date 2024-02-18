from typing import List, Union

from webql.common.errors import QuerySyntaxError

from .lexer import Lexer
from .node import ContainerListNode, ContainerNode, IdListNode, IdNode, Node
from .source import Source
from .token import Token
from .token_kind import TokenKind


class Parser:
    """A parser for WebQL queries. It is a recursive descent parser, which is a top-down parser that
    uses a set of recursive procedures to process the input."""

    def __init__(self, source: Union[Source, str]) -> None:
        """Initialize the parser.

        Parameters:

        source (Source | str): The source of the query."""
        self.source = isinstance(source, Source) and source or Source(source)
        self.lexer = Lexer(self.source)

    def parse(self) -> ContainerNode:
        """Parses the source and check for syntax. It is the entry point of the parser."""
        self._expect_token(TokenKind.SOF)
        node = self._parse_container()
        self._expect_token(TokenKind.EOF)
        return node

    def _parse_container(self, name: str = "") -> ContainerNode:
        """Parses a container, which is enclosed by curly braces."""

        nodes = self._many(TokenKind.BRACE_L, self._parse_identifier, TokenKind.BRACE_R)
        return ContainerNode(name=name, children=nodes)

    def _parse_identifier(self) -> Node:
        """Parses an identifier."""
        name = self._expect_token(TokenKind.IDENTIFIER).value

        if self._peek(TokenKind.BRACE_L):
            node = self._parse_container(name)
        elif self._peek(TokenKind.BRACKET_L):
            node = self._parse_list(name)
        else:
            node = IdNode(name=name)
        return node

    def _parse_list(self, name: str) -> Union[ContainerListNode, IdListNode]:
        """Parses a list, represented by two brackets."""
        prev_token = self.lexer.token.prev
        # make sure list token is following an identifier
        if prev_token.kind != TokenKind.IDENTIFIER:
            error_message = f"Expected Identifier, found {prev_token.kind.value} on row {prev_token.line}. List token ([]) must follow an identifier."
            raise QuerySyntaxError(
                message=error_message,
                unexpected_token=prev_token.kind.value,
                row=prev_token.line,
                column=prev_token.column,
            )

        self._expect_token(TokenKind.BRACKET_L)
        self._expect_token(TokenKind.BRACKET_R)

        if self._peek(TokenKind.BRACE_L):
            container = self._parse_container(name)
            node = ContainerListNode(name=container.name, children=container.children)
        else:
            node = IdListNode(name=name)
        return node

    def _many(
        self, open_kind: TokenKind, parse_fn: callable, close_kind: TokenKind, **kwargs
    ) -> List[Node]:
        """Parses zero or more tokens of the given kind by repeatedly calling the given
        parse function. Check whether the syntax is valid."""
        self._expect_token(open_kind)
        identifier_name_list = set()
        nodes = []

        while True:
            # make sure there is no duplicate identifier in the same container
            if self._peek(TokenKind.IDENTIFIER):
                identifier = self.lexer.token.value
                if identifier in identifier_name_list:
                    error_message = f"Duplicate identifier '{identifier}' on row {self.lexer.token.line}. Identifier must be unique in the same container."
                    raise QuerySyntaxError(
                        error_message,
                        unexpected_token=identifier,
                        row=self.lexer.token.line,
                        column=self.lexer.token.column,
                    )
                identifier_name_list.add(identifier)

            nodes.append(parse_fn(**kwargs))

            if self._peek(close_kind):
                self.lexer.advance()
                break

        return nodes

    def _expect_token(self, kind: TokenKind) -> Token:
        """Consumes the next token if it matches the given kind, otherwise throws an
        error.
        """
        token = self.lexer.token
        if token.kind == kind:
            self.lexer.advance()
            return token

        error_message = f"Expected {kind.value}, found {token.kind.value} on row {token.line}"
        raise QuerySyntaxError(
            error_message,
            unexpected_token=kind.value,
            row=token.line,
            column=token.column,
        )

    def _peek(self, kind: TokenKind) -> bool:
        """Returns "true" if the next token is of the given kind."""
        return self.lexer.token.kind == kind
