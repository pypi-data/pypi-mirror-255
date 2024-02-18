from abc import ABCMeta as ABCMeta12
from builtins import str as str2, bool as bool0, int as int9, Exception as Exception8, RuntimeError as RuntimeError11, len as len_1248, list as list_1243
from types import MappingProxyType as MappingProxyType13
from typing import Callable as Callable3, Sequence as Sequence4, Optional as Optional6, Union as Union5, Any as Any7, MutableSequence as MutableSequence1
from temper_core import cast_by_type as cast_by_type14, Label as Label10, isinstance_int as isinstance_int15, cast_by_test as cast_by_test16, list_join as list_join_1242, generic_eq as generic_eq_1258, list_builder_add as list_builder_add_1238, string_code_points as string_code_points_1261, list_get as list_get_1249, str_cat as str_cat_1251, int_to_string as int_to_string_1274
from temper_core.regex import compiled_regex_compile_formatted as compiled_regex_compile_formatted_1252, compiled_regex_compiled_found as compiled_regex_compiled_found_1253, compiled_regex_compiled_find as compiled_regex_compiled_find_1254, compiled_regex_compiled_replace as compiled_regex_compiled_replace_1255, regex_formatter_push_capture_name as regex_formatter_push_capture_name_1259, regex_formatter_push_code_to as regex_formatter_push_code_to_1260
class Regex(metaclass = ABCMeta12):
  def compiled(this__8) -> 'CompiledRegex':
    return CompiledRegex(this__8)
  def found(this__9, text__121: 'str2') -> 'bool0':
    return this__9.compiled().found(text__121)
  def find(this__10, text__124: 'str2') -> 'MappingProxyType13[str2, Group]':
    return this__10.compiled().find(text__124)
  def replace(this__11, text__127: 'str2', format__128: 'Callable3[[MappingProxyType13[str2, Group]], str2]') -> 'str2':
    return this__11.compiled().replace(text__127, format__128)
class Capture(Regex):
  name__130: 'str2'
  item__131: 'Regex'
  __slots__ = ('name__130', 'item__131')
  def constructor__132(this__50, name__133: 'str2', item__134: 'Regex') -> 'None':
    this__50.name__130 = name__133
    this__50.item__131 = item__134
  def __init__(this__50, name__133: 'str2', item__134: 'Regex') -> None:
    this__50.constructor__132(name__133, item__134)
  @property
  def name(this__298) -> 'str2':
    return this__298.name__130
  @property
  def item(this__302) -> 'Regex':
    return this__302.item__131
class CodePart(Regex, metaclass = ABCMeta12):
  pass
class CodePoints(CodePart):
  value__135: 'str2'
  __slots__ = ('value__135',)
  def constructor__136(this__52, value__137: 'str2') -> 'None':
    this__52.value__135 = value__137
  def __init__(this__52, value__137: 'str2') -> None:
    this__52.constructor__136(value__137)
  @property
  def value(this__306) -> 'str2':
    return this__306.value__135
class Special(Regex, metaclass = ABCMeta12):
  pass
class SpecialSet(CodePart, Special, metaclass = ABCMeta12):
  pass
class CodeRange(CodePart):
  min__145: 'int9'
  max__146: 'int9'
  __slots__ = ('min__145', 'max__146')
  def constructor__147(this__68, min__148: 'int9', max__149: 'int9') -> 'None':
    this__68.min__145 = min__148
    this__68.max__146 = max__149
  def __init__(this__68, min__148: 'int9', max__149: 'int9') -> None:
    this__68.constructor__147(min__148, max__149)
  @property
  def min(this__310) -> 'int9':
    return this__310.min__145
  @property
  def max(this__314) -> 'int9':
    return this__314.max__146
class CodeSet(Regex):
  items__150: 'Sequence4[CodePart]'
  negated__151: 'bool0'
  __slots__ = ('items__150', 'negated__151')
  def constructor__152(this__70, items__153: 'Sequence4[CodePart]', negated: Optional6['bool0'] = None) -> 'None':
    negated__154: Optional6['bool0'] = negated
    if negated__154 is None:
      negated__154 = False
    this__70.items__150 = items__153
    this__70.negated__151 = negated__154
  def __init__(this__70, items__153: 'Sequence4[CodePart]', negated: Optional6['bool0'] = None) -> None:
    negated__154: Optional6['bool0'] = negated
    this__70.constructor__152(items__153, negated__154)
  @property
  def items(this__318) -> 'Sequence4[CodePart]':
    return this__318.items__150
  @property
  def negated(this__322) -> 'bool0':
    return this__322.negated__151
class Or(Regex):
  items__155: 'Sequence4[Regex]'
  __slots__ = ('items__155',)
  def constructor__156(this__73, items__157: 'Sequence4[Regex]') -> 'None':
    this__73.items__155 = items__157
  def __init__(this__73, items__157: 'Sequence4[Regex]') -> None:
    this__73.constructor__156(items__157)
  @property
  def items(this__326) -> 'Sequence4[Regex]':
    return this__326.items__155
class Repeat(Regex):
  item__158: 'Regex'
  min__159: 'int9'
  max__160: 'Union5[int9, None]'
  reluctant__161: 'bool0'
  __slots__ = ('item__158', 'min__159', 'max__160', 'reluctant__161')
  def constructor__162(this__76, item__163: 'Regex', min__164: 'int9', max__165: 'Union5[int9, None]', reluctant: Optional6['bool0'] = None) -> 'None':
    reluctant__166: Optional6['bool0'] = reluctant
    if reluctant__166 is None:
      reluctant__166 = False
    this__76.item__158 = item__163
    this__76.min__159 = min__164
    this__76.max__160 = max__165
    this__76.reluctant__161 = reluctant__166
  def __init__(this__76, item__163: 'Regex', min__164: 'int9', max__165: 'Union5[int9, None]', reluctant: Optional6['bool0'] = None) -> None:
    reluctant__166: Optional6['bool0'] = reluctant
    this__76.constructor__162(item__163, min__164, max__165, reluctant__166)
  @property
  def item(this__330) -> 'Regex':
    return this__330.item__158
  @property
  def min(this__334) -> 'int9':
    return this__334.min__159
  @property
  def max(this__338) -> 'Union5[int9, None]':
    return this__338.max__160
  @property
  def reluctant(this__342) -> 'bool0':
    return this__342.reluctant__161
class Sequence(Regex):
  items__175: 'Sequence4[Regex]'
  __slots__ = ('items__175',)
  def constructor__176(this__82, items__177: 'Sequence4[Regex]') -> 'None':
    this__82.items__175 = items__177
  def __init__(this__82, items__177: 'Sequence4[Regex]') -> None:
    this__82.constructor__176(items__177)
  @property
  def items(this__346) -> 'Sequence4[Regex]':
    return this__346.items__175
class Group:
  name__178: 'str2'
  value__179: 'str2'
  codePointsBegin__180: 'int9'
  __slots__ = ('name__178', 'value__179', 'codePointsBegin__180')
  def constructor__181(this__85, name__182: 'str2', value__183: 'str2', codePointsBegin__184: 'int9') -> 'None':
    this__85.name__178 = name__182
    this__85.value__179 = value__183
    this__85.codePointsBegin__180 = codePointsBegin__184
  def __init__(this__85, name__182: 'str2', value__183: 'str2', codePointsBegin__184: 'int9') -> None:
    this__85.constructor__181(name__182, value__183, codePointsBegin__184)
  @property
  def name(this__350) -> 'str2':
    return this__350.name__178
  @property
  def value(this__354) -> 'str2':
    return this__354.value__179
  @property
  def code_points_begin(this__358) -> 'int9':
    return this__358.codePointsBegin__180
class RegexRefs__19:
  codePoints__185: 'CodePoints'
  group__186: 'Group'
  orObject__187: 'Or'
  __slots__ = ('codePoints__185', 'group__186', 'orObject__187')
  def constructor__188(this__87, code_points: Optional6['CodePoints'] = None, group: Optional6['Group'] = None, or_object: Optional6['Or'] = None) -> 'None':
    codePoints__189: Optional6['CodePoints'] = code_points
    group__190: Optional6['Group'] = group
    orObject__191: Optional6['Or'] = or_object
    t_1164: 'CodePoints'
    t_1166: 'Group'
    t_1168: 'Or'
    if codePoints__189 is None:
      t_1164 = CodePoints('')
      codePoints__189 = t_1164
    if group__190 is None:
      t_1166 = Group('', '', 0)
      group__190 = t_1166
    if orObject__191 is None:
      t_1168 = Or(())
      orObject__191 = t_1168
    this__87.codePoints__185 = codePoints__189
    this__87.group__186 = group__190
    this__87.orObject__187 = orObject__191
  def __init__(this__87, code_points: Optional6['CodePoints'] = None, group: Optional6['Group'] = None, or_object: Optional6['Or'] = None) -> None:
    codePoints__189: Optional6['CodePoints'] = code_points
    group__190: Optional6['Group'] = group
    orObject__191: Optional6['Or'] = or_object
    this__87.constructor__188(codePoints__189, group__190, orObject__191)
  @property
  def code_points(this__362) -> 'CodePoints':
    return this__362.codePoints__185
  @property
  def group(this__366) -> 'Group':
    return this__366.group__186
  @property
  def or_object(this__370) -> 'Or':
    return this__370.orObject__187
class CompiledRegex:
  data__192: 'Regex'
  compiled__206: 'Any7'
  __slots__ = ('data__192', 'compiled__206')
  def constructor__193(this__20, data__194: 'Regex') -> 'None':
    this__20.data__192 = data__194
    t_1158: 'str2' = this__20.format__225()
    t_1159: 'Any7' = compiled_regex_compile_formatted_1252(this__20, t_1158)
    this__20.compiled__206 = t_1159
  def __init__(this__20, data__194: 'Regex') -> None:
    this__20.constructor__193(data__194)
  def found(this__21, text__197: 'str2') -> 'bool0':
    return compiled_regex_compiled_found_1253(this__21, this__21.compiled__206, text__197)
  def find(this__22, text__200: 'str2') -> 'MappingProxyType13[str2, Group]':
    return compiled_regex_compiled_find_1254(this__22, this__22.compiled__206, text__200, regexRefs__117)
  def replace(this__23, text__203: 'str2', format__204: 'Callable3[[MappingProxyType13[str2, Group]], str2]') -> 'str2':
    return compiled_regex_compiled_replace_1255(this__23, this__23.compiled__206, text__203, format__204, regexRefs__117)
  def format__225(this__28) -> 'str2':
    return RegexFormatter__29().format(this__28.data__192)
  @property
  def data(this__374) -> 'Regex':
    return this__374.data__192
class RegexFormatter__29:
  out__227: 'MutableSequence1[str2]'
  __slots__ = ('out__227',)
  def format(this__30, regex__229: 'Regex') -> 'str2':
    this__30.pushRegex__232(regex__229)
    t_1141: 'MutableSequence1[str2]' = this__30.out__227
    def fn__1138(x__231: 'str2') -> 'str2':
      return x__231
    return list_join_1242(t_1141, '', fn__1138)
  def pushRegex__232(this__31, regex__233: 'Regex') -> 'None':
    t_744: 'bool0'
    t_745: 'Capture'
    t_748: 'bool0'
    t_749: 'CodePoints'
    t_752: 'bool0'
    t_753: 'CodeRange'
    t_756: 'bool0'
    t_757: 'CodeSet'
    t_760: 'bool0'
    t_761: 'Or'
    t_764: 'bool0'
    t_765: 'Repeat'
    t_768: 'bool0'
    t_769: 'Sequence'
    try:
      cast_by_type14(regex__233, Capture)
      t_744 = True
    except Exception8:
      t_744 = False
    with Label10() as s__1256_1257:
      if t_744:
        try:
          t_745 = cast_by_type14(regex__233, Capture)
        except Exception8:
          s__1256_1257.break_()
        this__31.pushCapture__235(t_745)
      else:
        try:
          cast_by_type14(regex__233, CodePoints)
          t_748 = True
        except Exception8:
          t_748 = False
        if t_748:
          try:
            t_749 = cast_by_type14(regex__233, CodePoints)
          except Exception8:
            s__1256_1257.break_()
          this__31.pushCodePoints__251(t_749, False)
        else:
          try:
            cast_by_type14(regex__233, CodeRange)
            t_752 = True
          except Exception8:
            t_752 = False
          if t_752:
            try:
              t_753 = cast_by_type14(regex__233, CodeRange)
            except Exception8:
              s__1256_1257.break_()
            this__31.pushCodeRange__256(t_753)
          else:
            try:
              cast_by_type14(regex__233, CodeSet)
              t_756 = True
            except Exception8:
              t_756 = False
            if t_756:
              try:
                t_757 = cast_by_type14(regex__233, CodeSet)
              except Exception8:
                s__1256_1257.break_()
              this__31.pushCodeSet__262(t_757)
            else:
              try:
                cast_by_type14(regex__233, Or)
                t_760 = True
              except Exception8:
                t_760 = False
              if t_760:
                try:
                  t_761 = cast_by_type14(regex__233, Or)
                except Exception8:
                  s__1256_1257.break_()
                this__31.pushOr__274(t_761)
              else:
                try:
                  cast_by_type14(regex__233, Repeat)
                  t_764 = True
                except Exception8:
                  t_764 = False
                if t_764:
                  try:
                    t_765 = cast_by_type14(regex__233, Repeat)
                  except Exception8:
                    s__1256_1257.break_()
                  this__31.pushRepeat__278(t_765)
                else:
                  try:
                    cast_by_type14(regex__233, Sequence)
                    t_768 = True
                  except Exception8:
                    t_768 = False
                  if t_768:
                    try:
                      t_769 = cast_by_type14(regex__233, Sequence)
                    except Exception8:
                      s__1256_1257.break_()
                    this__31.pushSequence__283(t_769)
                  elif generic_eq_1258(regex__233, begin):
                    try:
                      list_builder_add_1238(this__31.out__227, '^')
                    except Exception8:
                      s__1256_1257.break_()
                  elif generic_eq_1258(regex__233, dot):
                    try:
                      list_builder_add_1238(this__31.out__227, '.')
                    except Exception8:
                      s__1256_1257.break_()
                  elif generic_eq_1258(regex__233, end):
                    try:
                      list_builder_add_1238(this__31.out__227, '$')
                    except Exception8:
                      s__1256_1257.break_()
                  elif generic_eq_1258(regex__233, word_boundary):
                    try:
                      list_builder_add_1238(this__31.out__227, '\\b')
                    except Exception8:
                      s__1256_1257.break_()
                  elif generic_eq_1258(regex__233, digit):
                    try:
                      list_builder_add_1238(this__31.out__227, '\\d')
                    except Exception8:
                      s__1256_1257.break_()
                  elif generic_eq_1258(regex__233, space):
                    try:
                      list_builder_add_1238(this__31.out__227, '\\s')
                    except Exception8:
                      s__1256_1257.break_()
                  elif generic_eq_1258(regex__233, word):
                    try:
                      list_builder_add_1238(this__31.out__227, '\\w')
                    except Exception8:
                      s__1256_1257.break_()
                  else:
                    None
      return
    raise RuntimeError11()
  def pushCapture__235(this__32, capture__236: 'Capture') -> 'None':
    t_1125: 'str2'
    t_1126: 'Regex'
    t_739: 'MutableSequence1[str2]'
    list_builder_add_1238(this__32.out__227, '(')
    t_739 = this__32.out__227
    t_1125 = capture__236.name
    regex_formatter_push_capture_name_1259(this__32, t_739, t_1125)
    t_1126 = capture__236.item
    this__32.pushRegex__232(t_1126)
    list_builder_add_1238(this__32.out__227, ')')
  def pushCode__242(this__34, code__243: 'int9', insideCodeSet__244: 'bool0') -> 'None':
    regex_formatter_push_code_to_1260(this__34, this__34.out__227, code__243, insideCodeSet__244)
  def pushCodePoints__251(this__36, codePoints__252: 'CodePoints', insideCodeSet__253: 'bool0') -> 'None':
    t_1114: 'int9'
    t_1115: 'Any7'
    t_1119: 'Any7' = string_code_points_1261(codePoints__252.value)
    slice__255: 'Any7' = t_1119
    while True:
      if not slice__255.is_empty:
        t_1114 = slice__255.read()
        this__36.pushCode__242(t_1114, insideCodeSet__253)
        t_1115 = slice__255.advance(1)
        slice__255 = t_1115
      else:
        break
  def pushCodeRange__256(this__37, codeRange__257: 'CodeRange') -> 'None':
    list_builder_add_1238(this__37.out__227, '[')
    this__37.pushCodeRangeUnwrapped__259(codeRange__257)
    list_builder_add_1238(this__37.out__227, ']')
  def pushCodeRangeUnwrapped__259(this__38, codeRange__260: 'CodeRange') -> 'None':
    t_1109: 'int9'
    t_1107: 'int9' = codeRange__260.min
    this__38.pushCode__242(t_1107, True)
    list_builder_add_1238(this__38.out__227, '-')
    t_1109 = codeRange__260.max
    this__38.pushCode__242(t_1109, True)
  def pushCodeSet__262(this__39, codeSet__263: 'CodeSet') -> 'None':
    t_1103: 'int9'
    t_717: 'bool0'
    t_718: 'CodeSet'
    t_723: 'CodePart'
    adjusted__265: 'Regex' = this__39.adjustCodeSet__267(codeSet__263, regexRefs__117)
    try:
      cast_by_type14(adjusted__265, CodeSet)
      t_717 = True
    except Exception8:
      t_717 = False
    with Label10() as s__1262_1264:
      if t_717:
        with Label10() as s__1263_1265:
          try:
            t_718 = cast_by_type14(adjusted__265, CodeSet)
            list_builder_add_1238(this__39.out__227, '[')
          except Exception8:
            s__1263_1265.break_()
          if t_718.negated:
            try:
              list_builder_add_1238(this__39.out__227, '^')
            except Exception8:
              s__1263_1265.break_()
          else:
            None
          i__266: 'int9' = 0
          while True:
            t_1103 = len_1248(t_718.items)
            if i__266 < t_1103:
              try:
                t_723 = list_get_1249(t_718.items, i__266)
              except Exception8:
                s__1263_1265.break_()
              this__39.pushCodeSetItem__271(t_723)
              i__266 = i__266 + 1
            else:
              break
          try:
            list_builder_add_1238(this__39.out__227, ']')
            s__1262_1264.break_()
          except Exception8:
            pass
        raise RuntimeError11()
      this__39.pushRegex__232(adjusted__265)
  def adjustCodeSet__267(this__40, codeSet__268: 'CodeSet', regexRefs__269: 'RegexRefs__19') -> 'Regex':
    return codeSet__268
  def pushCodeSetItem__271(this__41, codePart__272: 'CodePart') -> 'None':
    t_704: 'bool0'
    t_705: 'CodePoints'
    t_708: 'bool0'
    t_709: 'CodeRange'
    t_712: 'bool0'
    t_713: 'SpecialSet'
    try:
      cast_by_type14(codePart__272, CodePoints)
      t_704 = True
    except Exception8:
      t_704 = False
    with Label10() as s__1266_1267:
      if t_704:
        try:
          t_705 = cast_by_type14(codePart__272, CodePoints)
        except Exception8:
          s__1266_1267.break_()
        this__41.pushCodePoints__251(t_705, True)
      else:
        try:
          cast_by_type14(codePart__272, CodeRange)
          t_708 = True
        except Exception8:
          t_708 = False
        if t_708:
          try:
            t_709 = cast_by_type14(codePart__272, CodeRange)
          except Exception8:
            s__1266_1267.break_()
          this__41.pushCodeRangeUnwrapped__259(t_709)
        else:
          try:
            cast_by_type14(codePart__272, SpecialSet)
            t_712 = True
          except Exception8:
            t_712 = False
          if t_712:
            try:
              t_713 = cast_by_type14(codePart__272, SpecialSet)
            except Exception8:
              s__1266_1267.break_()
            this__41.pushRegex__232(t_713)
          else:
            None
      return
    raise RuntimeError11()
  def pushOr__274(this__42, or__275: 'Or') -> 'None':
    t_1087: 'int9'
    t_696: 'Regex'
    t_701: 'Regex'
    with Label10() as s__1268_1270:
      if not (not or__275.items):
        with Label10() as s__1269_1271:
          try:
            list_builder_add_1238(this__42.out__227, '(?:')
            t_696 = list_get_1249(or__275.items, 0)
          except Exception8:
            s__1269_1271.break_()
          this__42.pushRegex__232(t_696)
          i__277: 'int9' = 1
          while True:
            t_1087 = len_1248(or__275.items)
            if i__277 < t_1087:
              try:
                list_builder_add_1238(this__42.out__227, '|')
                t_701 = list_get_1249(or__275.items, i__277)
              except Exception8:
                break
              this__42.pushRegex__232(t_701)
              i__277 = i__277 + 1
            else:
              try:
                list_builder_add_1238(this__42.out__227, ')')
              except Exception8:
                s__1269_1271.break_()
              s__1268_1270.break_()
        raise RuntimeError11()
  def pushRepeat__278(this__43, repeat__279: 'Repeat') -> 'None':
    t_1077: 'Regex'
    t_683: 'bool0'
    t_684: 'bool0'
    t_685: 'bool0'
    t_688: 'int9'
    t_690: 'MutableSequence1[str2]'
    with Label10() as s__1272_1273:
      min__281: 'int9'
      max__282: 'Union5[int9, None]'
      try:
        list_builder_add_1238(this__43.out__227, '(?:')
        t_1077 = repeat__279.item
        this__43.pushRegex__232(t_1077)
        list_builder_add_1238(this__43.out__227, ')')
        min__281 = repeat__279.min
        max__282 = repeat__279.max
      except Exception8:
        s__1272_1273.break_()
      if min__281 == 0:
        t_683 = max__282 == 1
      else:
        t_683 = False
      if t_683:
        try:
          list_builder_add_1238(this__43.out__227, '?')
        except Exception8:
          s__1272_1273.break_()
      else:
        if min__281 == 0:
          t_684 = max__282 == None
        else:
          t_684 = False
        if t_684:
          try:
            list_builder_add_1238(this__43.out__227, '*')
          except Exception8:
            s__1272_1273.break_()
        else:
          if min__281 == 1:
            t_685 = max__282 == None
          else:
            t_685 = False
          if t_685:
            try:
              list_builder_add_1238(this__43.out__227, '+')
            except Exception8:
              s__1272_1273.break_()
          else:
            try:
              list_builder_add_1238(this__43.out__227, str_cat_1251('{', int_to_string_1274(min__281)))
            except Exception8:
              s__1272_1273.break_()
            if min__281 != max__282:
              try:
                list_builder_add_1238(this__43.out__227, ',')
              except Exception8:
                s__1272_1273.break_()
              if max__282 != None:
                t_690 = this__43.out__227
                try:
                  t_688 = cast_by_test16(max__282, isinstance_int15)
                  list_builder_add_1238(t_690, int_to_string_1274(t_688))
                except Exception8:
                  s__1272_1273.break_()
              else:
                None
            else:
              None
            try:
              list_builder_add_1238(this__43.out__227, '}')
            except Exception8:
              s__1272_1273.break_()
      if repeat__279.reluctant:
        try:
          list_builder_add_1238(this__43.out__227, '?')
        except Exception8:
          s__1272_1273.break_()
      else:
        None
      return
    raise RuntimeError11()
  def pushSequence__283(this__44, sequence__284: 'Sequence') -> 'None':
    t_1075: 'int9'
    t_677: 'Regex'
    i__286: 'int9' = 0
    with Label10() as s__1275_1276:
      while True:
        t_1075 = len_1248(sequence__284.items)
        if i__286 < t_1075:
          try:
            t_677 = list_get_1249(sequence__284.items, i__286)
          except Exception8:
            break
          this__44.pushRegex__232(t_677)
          i__286 = i__286 + 1
        else:
          s__1275_1276.break_()
      raise RuntimeError11()
  def max_code(this__45, codePart__288: 'CodePart') -> 'Union5[int9, None]':
    return__116: 'Union5[int9, None]'
    t_1053: 'Any7'
    t_1055: 'Any7'
    t_1060: 'Union5[int9, None]'
    t_1063: 'Union5[int9, None]'
    t_1066: 'Union5[int9, None]'
    t_1069: 'Union5[int9, None]'
    t_650: 'bool0'
    t_651: 'CodePoints'
    t_663: 'bool0'
    t_664: 'CodeRange'
    try:
      cast_by_type14(codePart__288, CodePoints)
      t_650 = True
    except Exception8:
      t_650 = False
    with Label10() as s__1277_1278:
      if t_650:
        try:
          t_651 = cast_by_type14(codePart__288, CodePoints)
        except Exception8:
          s__1277_1278.break_()
        value__290: 'str2' = t_651.value
        if not value__290:
          return__116 = None
        else:
          max__291: 'int9' = 0
          t_1053 = string_code_points_1261(value__290)
          slice__292: 'Any7' = t_1053
          while True:
            if not slice__292.is_empty:
              next__293: 'int9' = slice__292.read()
              if next__293 > max__291:
                max__291 = next__293
              else:
                None
              t_1055 = slice__292.advance(1)
              slice__292 = t_1055
            else:
              break
          return__116 = max__291
      else:
        try:
          cast_by_type14(codePart__288, CodeRange)
          t_663 = True
        except Exception8:
          t_663 = False
        if t_663:
          try:
            t_664 = cast_by_type14(codePart__288, CodeRange)
            t_1060 = t_664.max
            return__116 = t_1060
          except Exception8:
            s__1277_1278.break_()
        elif generic_eq_1258(codePart__288, digit):
          t_1063 = string_code_points_1261('9').read()
          try:
            return__116 = t_1063
          except Exception8:
            s__1277_1278.break_()
        elif generic_eq_1258(codePart__288, space):
          t_1066 = string_code_points_1261(' ').read()
          try:
            return__116 = t_1066
          except Exception8:
            s__1277_1278.break_()
        elif generic_eq_1258(codePart__288, word):
          t_1069 = string_code_points_1261('z').read()
          try:
            return__116 = t_1069
          except Exception8:
            s__1277_1278.break_()
        else:
          return__116 = None
      return return__116
    raise RuntimeError11()
  def constructor__294(this__98, out: Optional6['MutableSequence1[str2]'] = None) -> 'None':
    out__295: Optional6['MutableSequence1[str2]'] = out
    t_1049: 'MutableSequence1[str2]'
    if out__295 is None:
      t_1049 = list_1243()
      out__295 = t_1049
    this__98.out__227 = out__295
  def __init__(this__98, out: Optional6['MutableSequence1[str2]'] = None) -> None:
    out__295: Optional6['MutableSequence1[str2]'] = out
    this__98.constructor__294(out__295)
class Begin__12(Special):
  __slots__ = ()
  def constructor__138(this__54) -> 'None':
    None
  def __init__(this__54) -> None:
    this__54.constructor__138()
begin: 'Special' = Begin__12()
class Dot__13(Special):
  __slots__ = ()
  def constructor__139(this__56) -> 'None':
    None
  def __init__(this__56) -> None:
    this__56.constructor__139()
dot: 'Special' = Dot__13()
class End__14(Special):
  __slots__ = ()
  def constructor__140(this__58) -> 'None':
    None
  def __init__(this__58) -> None:
    this__58.constructor__140()
end: 'Special' = End__14()
class WordBoundary__15(Special):
  __slots__ = ()
  def constructor__141(this__60) -> 'None':
    None
  def __init__(this__60) -> None:
    this__60.constructor__141()
word_boundary: 'Special' = WordBoundary__15()
class Digit__16(SpecialSet):
  __slots__ = ()
  def constructor__142(this__62) -> 'None':
    None
  def __init__(this__62) -> None:
    this__62.constructor__142()
digit: 'SpecialSet' = Digit__16()
class Space__17(SpecialSet):
  __slots__ = ()
  def constructor__143(this__64) -> 'None':
    None
  def __init__(this__64) -> None:
    this__64.constructor__143()
space: 'SpecialSet' = Space__17()
class Word__18(SpecialSet):
  __slots__ = ()
  def constructor__144(this__66) -> 'None':
    None
  def __init__(this__66) -> None:
    this__66.constructor__144()
word: 'SpecialSet' = Word__18()
def entire(item__167: 'Regex') -> 'Regex':
  global begin, end
  return Sequence((begin, item__167, end))
def one_or_more(item__169: 'Regex', reluctant: Optional6['bool0'] = None) -> 'Repeat':
  reluctant__170: Optional6['bool0'] = reluctant
  if reluctant__170 is None:
    reluctant__170 = False
  return Repeat(item__169, 1, None, reluctant__170)
def optional(item__172: 'Regex', reluctant: Optional6['bool0'] = None) -> 'Repeat':
  reluctant__173: Optional6['bool0'] = reluctant
  if reluctant__173 is None:
    reluctant__173 = False
  return Repeat(item__172, 0, 1, reluctant__173)
regexRefs__117: 'RegexRefs__19' = RegexRefs__19()
