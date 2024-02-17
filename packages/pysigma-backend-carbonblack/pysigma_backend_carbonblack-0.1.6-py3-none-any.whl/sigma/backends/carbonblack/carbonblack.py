from sigma.conversion.state import ConversionState
from sigma.rule import SigmaRule
from sigma.conversion.base import TextQueryBackend
from sigma.conditions import ConditionItem, ConditionAND, ConditionOR, ConditionNOT, ConditionFieldEqualsValueExpression
from sigma.types import SigmaCompareExpression, SigmaRegularExpression, SigmaRegularExpressionFlag, SigmaString
from sigma.conversion.deferred import DeferredQueryExpression
from sigma.processing.pipeline import ProcessingPipeline
import sigma
import re
from typing import ClassVar, Dict, Tuple, Pattern, List, Any, Union

class CarbonBlackBackend(TextQueryBackend):
    """CarbonBlack backend."""

    name : ClassVar[str] = "CarbonBlack backend"
    formats : Dict[str, str] = {
        "default": "Plain CarbonBlack queries",
        "json": "CarbonBlack JSON query",
    }

    requires_pipeline : bool = False

    precedence : ClassVar[Tuple[ConditionItem, ConditionItem, ConditionItem]] = (ConditionNOT, ConditionAND, ConditionOR)
    group_expression : ClassVar[str] = "({expr})"   # Expression for precedence override grouping as format string with {expr} placeholder
    parenthesize : bool = True

    token_separator : str = " "     # separator inserted between all boolean operators
    or_token : ClassVar[str] = "OR"
    and_token : ClassVar[str] = " "
    not_token : ClassVar[str] = "-"
    eq_token : ClassVar[str] = ":"  # Token inserted between field and value (without separator)

    field_quote : ClassVar[str] = '"'                              # Character used to quote field characters if field_quote_pattern matches (or not, depending on field_quote_pattern_negation). No field name quoting is done if not set.
    field_quote_pattern : ClassVar[Pattern] = re.compile("^\\w+$")   # Quote field names if this pattern (doesn't) matches, depending on field_quote_pattern_negation. Field name is always quoted if pattern is not set.
    field_quote_pattern_negation : ClassVar[bool] = True            # Negate field_quote_pattern result. Field name is quoted if pattern doesn't matches if set to True (default).

    field_escape : ClassVar[str] = "\\"               # Character to escape particular parts defined in field_escape_pattern.
    field_escape_quote : ClassVar[bool] = True        # Escape quote string defined in field_quote
    field_escape_pattern : ClassVar[Pattern] = re.compile("\\s")   # All matches of this pattern are prepended with the string contained in field_escape.

    str_quote       : ClassVar[str] = ''     # string quoting character (added as escaping character)
    escape_char     : ClassVar[str] = "\\"    # Escaping character for special characrers inside string
    wildcard_multi  : ClassVar[str] = "*"     # Character used as multi-character wildcard
    wildcard_single : ClassVar[str] = "*"     # Character used as single-character wildcard
    add_escaped     : ClassVar[str] = " "    # Characters quoted in addition to wildcards and string quote
    filter_chars    : ClassVar[str] = ""      # Characters filtered
    bool_values     : ClassVar[Dict[bool, str]] = {   # Values to which boolean values are mapped.
        True: "TRUE",
        False: "FALSE",
    }

    re_expression : ClassVar[str] = "{field}:{regex}"
    re_escape_char : ClassVar[str] = "\\"               # Character used for escaping in regular expressions
    re_escape : ClassVar[Tuple[str]] = ()               # List of strings that are escaped
    re_escape_escape_char : bool = True                 # If True, the escape character is also escaped
    re_flag_prefix : bool = False                        # If True, the flags are prepended as (?x) group at the beginning of the regular expression, e.g. (?i). If this is not supported by the target, it should be set to False.


    compare_op_expression : ClassVar[str] = "{field}:{value}"

    field_exists_expression : ClassVar[str] = "{field}:*"             # Expression for field existence as format string with {field} placeholder for field name
    field_not_exists_expression : ClassVar[str] = "-{field}:*"      # Expression for field non-existence as format string with {field} placeholder for field name. If not set, field_exists_expression is negated with boolean NOT.

    convert_or_as_in : ClassVar[bool] = False                     # Convert OR as in-expression
    convert_and_as_in : ClassVar[bool] = False                    # Convert AND as in-expression
    in_expressions_allow_wildcards : ClassVar[bool] = False       # Values in list can contain wildcards. If set to False (default) only plain values are converted into in-expressions.

    unbound_value_str_expression : ClassVar[str] = '"{value}"'   # Expression for string value not bound to a field as format string with placeholder {value}
    unbound_value_num_expression : ClassVar[str] = '{value}'     # Expression for number value not bound to a field as format string with placeholder {value}
    unbound_value_re_expression : ClassVar[str] = '{value}'   # Expression for regular expression not bound to a field as format string with placeholder {value} and {flag_x} as described for re_expression

    def convert_value_str(self, s : SigmaString, state : ConversionState) -> str:
        """Convert a SigmaString into a plain string which can be used in query.
        In carbonBlack, leading wildcards are implied and not allowed to be explicitly added in the query"""
        converted = s.convert(
            self.escape_char,
            self.wildcard_multi,
            self.wildcard_single,
            self.str_quote + self.add_escaped,
            self.filter_chars,
        )
        if converted.startswith(self.wildcard_multi) or converted.startswith(self.wildcard_single):
            converted = converted[1:]

        if self.decide_string_quoting(s):
            return self.quote_string(converted)
        else:
            return converted

    def convert_condition_field_compare_op_val(self, cond : ConditionFieldEqualsValueExpression, state : ConversionState) -> Union[str, DeferredQueryExpression]:
        """Conversion of numeric comparison operations into queries.
        In CarbonBlack, ranges are handled slightly different than typical lt/gt operators
        """
        if cond.value.op == SigmaCompareExpression.CompareOperators.LT or cond.value.op == SigmaCompareExpression.CompareOperators.LTE:
            value = f'[* TO {cond.value.number}]'
        else:
            value = f'[{cond.value.number} TO *]'

        return self.compare_op_expression.format(
            field=self.escape_and_quote_field(cond.field),
            value = value
        )

    def convert_condition_not(self, cond: ConditionNOT, state: ConversionState) -> Union[str, DeferredQueryExpression]:
        """
        Conversion of NOT conditions.
        CarbonBlack is unique in that the NOT operator cannot have a space
        """
        arg = cond.args[0]
        try:
            if arg.__class__ in self.precedence:  # group if AND or OR condition is negated
                return (
                    self.not_token + self.convert_condition_group(arg, state)
                )
            else:
                expr = self.convert_condition(arg, state)
                if isinstance(
                    expr, DeferredQueryExpression
                ):  # negate deferred expression and pass it to parent
                    return expr.negate()
                else:  # convert negated expression to string
                    return self.not_token + expr
        except TypeError:  # pragma: no cover
            raise NotImplementedError("Operator 'not' not supported by the backend")

    def finalize_query_default(self, rule: SigmaRule, query: str, index: int, state: ConversionState) -> Any:
        return query

    def finalize_output_default(self, queries: List[str]) -> Any:
        return queries
    
    def finalize_query_json(self, rule: SigmaRule, query: str, index: int, state: ConversionState) -> Any:
        return {"query": query, 'title':rule.title, 'id':rule.id, 'description':rule.description}

    def finalize_output_json(self, queries: List[str]) -> Any:
        return {"queries":queries}
    
    