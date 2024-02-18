from builtins import bool as bool0, str as str2, Exception as Exception8, int as int9, RuntimeError as RuntimeError11, tuple as tuple_1240, list as list_1243, len as len_1248
from typing import MutableSequence as MutableSequence1, Callable as Callable3, Sequence as Sequence4, Union as Union5, Optional as Optional6, Any as Any7
from temper_core import Pair as Pair_1244, Label as Label10, list_builder_add as list_builder_add_1238, list_join as list_join_1242, list_map as list_map_1245, list_get as list_get_1249, str_cat as str_cat_1251
from temper_core import LoggingConsole
vGlobalConsole__47_1250 = LoggingConsole(__name__)
class Test:
  passing__16: 'bool0'
  failedOnAssert__17: 'bool0'
  hasUnhandledFail__18: 'bool0'
  _failedOnAssert__58: 'bool0'
  _passing__59: 'bool0'
  _messages__60: 'MutableSequence1[str2]'
  __slots__ = ('passing__16', 'failedOnAssert__17', 'hasUnhandledFail__18', '_failedOnAssert__58', '_passing__59', '_messages__60')
  def assert_(this__7, success__36: 'bool0', message__37: 'Callable3[[], str2]') -> 'None':
    if not success__36:
      this__7._passing__59 = False
      list_builder_add_1238(this__7._messages__60, message__37())
    else:
      None
  def assert_hard(this__8, success__40: 'bool0', message__41: 'Callable3[[], str2]') -> 'None':
    this__8.assert_(success__40, message__41)
    if not success__40:
      this__8._failedOnAssert__58 = True
      assert False, str2(this__8.messages_combined())
    else:
      None
  def soft_fail_to_hard(this__9) -> 'None':
    if this__9.has_unhandled_fail:
      this__9._failedOnAssert__58 = True
      assert False, str2(this__9.messages_combined())
    else:
      None
  @property
  def passing(this__11) -> 'bool0':
    return this__11._passing__59
  def messages(this__12) -> 'Sequence4[str2]':
    return tuple_1240(this__12._messages__60)
  @property
  def failed_on_assert(this__13) -> 'bool0':
    return this__13._failedOnAssert__58
  @property
  def has_unhandled_fail(this__14) -> 'bool0':
    t_184: 'bool0'
    if this__14._failedOnAssert__58:
      t_184 = True
    else:
      t_184 = this__14._passing__59
    return not t_184
  def messages_combined(this__15) -> 'Union5[str2, None]':
    return__30: 'Union5[str2, None]'
    t_287: 'MutableSequence1[str2]'
    t_288: 'Union5[str2, None]'
    if not this__15._messages__60:
      return__30 = None
    else:
      t_287 = this__15._messages__60
      def fn__284(it__57: 'str2') -> 'str2':
        return it__57
      t_288 = list_join_1242(t_287, ', ', fn__284)
      return__30 = t_288
    return return__30
  def constructor__61(this__19, failed_on_assert: Optional6['bool0'] = None, passing: Optional6['bool0'] = None, messages: Optional6['MutableSequence1[str2]'] = None) -> 'None':
    _failedOnAssert__62: Optional6['bool0'] = failed_on_assert
    _passing__63: Optional6['bool0'] = passing
    _messages__64: Optional6['MutableSequence1[str2]'] = messages
    t_281: 'MutableSequence1[str2]'
    if _failedOnAssert__62 is None:
      _failedOnAssert__62 = False
    if _passing__63 is None:
      _passing__63 = True
    if _messages__64 is None:
      t_281 = list_1243()
      _messages__64 = t_281
    this__19._failedOnAssert__58 = _failedOnAssert__62
    this__19._passing__59 = _passing__63
    this__19._messages__60 = _messages__64
  def __init__(this__19, failed_on_assert: Optional6['bool0'] = None, passing: Optional6['bool0'] = None, messages: Optional6['MutableSequence1[str2]'] = None) -> None:
    _failedOnAssert__62: Optional6['bool0'] = failed_on_assert
    _passing__63: Optional6['bool0'] = passing
    _messages__64: Optional6['MutableSequence1[str2]'] = messages
    this__19.constructor__61(_failedOnAssert__62, _passing__63, _messages__64)
test_name: 'Any7' = ('<<lang.temper.value.TType: Type, lang.temper.value.Value: String: Type>>', NotImplemented)[1]
test_fun: 'Any7' = ('<<lang.temper.value.TType: Type, lang.temper.value.Value: fn (Test): (Void | Bubble): Type>>', NotImplemented)[1]
test_case: 'Any7' = ('<<lang.temper.value.TType: Type, lang.temper.value.Value: Pair<String, fn (Test): (Void | Bubble)>: Type>>', NotImplemented)[1]
test_failure_message: 'Any7' = ('<<lang.temper.value.TType: Type, lang.temper.value.Value: String: Type>>', NotImplemented)[1]
test_result: 'Any7' = ('<<lang.temper.value.TType: Type, lang.temper.value.Value: Pair<String, List<String>>: Type>>', NotImplemented)[1]
def process_test_cases(testCases__65: 'Sequence4[(Pair_1244[str2, (Callable3[[Test], None])])]') -> 'Sequence4[(Pair_1244[str2, (Sequence4[str2])])]':
  global list_map_1245
  def fn__274(testCase__67: 'Pair_1244[str2, (Callable3[[Test], None])]') -> 'Pair_1244[str2, (Sequence4[str2])]':
    global Pair_1244, list_1243, list_builder_add_1238, tuple_1240
    t_265: 'bool0'
    t_267: 'Sequence4[str2]'
    t_166: 'bool0'
    key__69: 'str2' = testCase__67.key
    fun__70: 'Callable3[[Test], None]' = testCase__67.value
    test__71: 'Test' = Test()
    hadBubble__72: 'bool0'
    try:
      fun__70(test__71)
      hadBubble__72 = False
    except Exception8:
      hadBubble__72 = True
    messages__73: 'Sequence4[str2]' = test__71.messages()
    failures__74: 'Sequence4[str2]'
    if test__71.passing:
      failures__74 = ()
    else:
      if hadBubble__72:
        t_265 = test__71.failed_on_assert
        t_166 = not t_265
      else:
        t_166 = False
      if t_166:
        allMessages__75: 'MutableSequence1[str2]' = list_1243(messages__73)
        list_builder_add_1238(allMessages__75, 'Bubble')
        t_267 = tuple_1240(allMessages__75)
        failures__74 = t_267
      else:
        failures__74 = messages__73
    return Pair_1244(key__69, failures__74)
  return list_map_1245(testCases__65, fn__274)
def report_test_results(testResults__76: 'Sequence4[(Pair_1244[str2, (Sequence4[str2])])]') -> 'None':
  global len_1248, list_get_1249, list_join_1242, str_cat_1251, vGlobalConsole__47_1250
  t_252: 'int9'
  t_152: 'Pair_1244[str2, (Sequence4[str2])]'
  i__78: 'int9' = 0
  with Label10() as s__1246_1247:
    while True:
      t_252 = len_1248(testResults__76)
      if i__78 < t_252:
        try:
          t_152 = list_get_1249(testResults__76, i__78)
        except Exception8:
          break
        testResult__79: 'Pair_1244[str2, (Sequence4[str2])]' = t_152
        failureMessages__80: 'Sequence4[str2]' = testResult__79.value
        if not failureMessages__80:
          vGlobalConsole__47_1250.log(str_cat_1251(testResult__79.key, ': Passed'))
        else:
          def fn__250(it__82: 'str2') -> 'str2':
            return it__82
          message__81: 'str2' = list_join_1242(failureMessages__80, ', ', fn__250)
          vGlobalConsole__47_1250.log(str_cat_1251(testResult__79.key, ': Failed ', message__81))
        i__78 = i__78 + 1
      else:
        s__1246_1247.break_()
    raise RuntimeError11()
def run_test_cases(testCases__83: 'Sequence4[(Pair_1244[str2, (Callable3[[Test], None])])]') -> 'None':
  global process_test_cases, report_test_results
  report_test_results(process_test_cases(testCases__83))
def run_test(testFun__85: 'Callable3[[Test], None]') -> 'None':
  test__87: 'Test' = Test()
  testFun__85(test__87)
  test__87.soft_fail_to_hard()
