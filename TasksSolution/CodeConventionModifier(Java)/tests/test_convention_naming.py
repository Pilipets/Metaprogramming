from src.core.convention import get_convention_rename, ConventionNaming, NameType

const_vars_data = [
    ("Simple2sd3", "SIMPLE2_SD3"),
    ("__23Yet__234how223Foo_$var______", "YET_234HOW223_FOO_VAR"),
    ("_23dummy$___var23Or32This", "DUMMY_VAR23_OR32_THIS"),
    ("_23Dummy__23__easy", "DUMMY_23_EASY"),
    ("EasierWhy__$", "EASIER_WHY"),
    ("_23__Simpler___no", "SIMPLER_NO"),
    ("_234_Sowhat__$", "SOWHAT"),
    ("TakeItEasy", "TAKE_IT_EASY"),
    ("why_i", "WHY_I"),
    ("", ""),
    ("__$", ""),
    ("_23$", ""),
    ("BOARDSMANAGER", "BOARDSMANAGER")
]
def test_const_vars_rename():
    for _in, _out in const_vars_data:
        assert _out == ConventionNaming.get_constant_name(_in)
        assert _out == get_convention_rename(NameType.CONST_VARIABLE, _in)

class_vars_data = [
    ("__23Yet__234how223Foo_$var______", "Yet234how223FooVar"),
    ("_234_Sowhat__$", "Sowhat"),
    ("Var_2DIY2", "Var2DIY2"),
    ("VAR_2diy2", "VAR2diy2"), 
    ("_23dummy$___var23Or32This", "DummyVar23Or32This"),
    ("_23Dummy__23__easy", "Dummy23Easy"),
    ("Easier__WHY__$", "EasierWHY"),
    ("_23__Simpler___no", "SimplerNo"),
    ("SOWHAT", "SOWHAT"),
    ("TakeItEasy", "TakeItEasy"),
    ("BCLoader", "BCLoader"),
    ("why_i", "WhyI"),
    ("", ""),
    ("__$", ""),
    ("_23$", "")
]
def test_class_vars_rename():
    for _in, _out in class_vars_data:
        assert _out == ConventionNaming.get_class_name(_in)
        assert _out == get_convention_rename(NameType.CLASS, _in)

methods_data = [
    ("Var_2DIY2", "var2Diy2"),
    ("VAR_2diy2", "var2diy2"),
    ("_23dummy$___var23Or32This", "dummyVar23Or32This"),
    ("_23Dummy__23__easy", "dummy23Easy"),
    ("Easier__WHY__$", "easierWhy"),
    ("_23__Simpler___no", "simplerNo"),
    ("_234_Sowhat__$", "sowhat"),
    ("TakeItEasy", "takeItEasy"),
    ("why_i", "whyI"),
    ("__23Yet__234how223Foo_$var______", "yet234how223FooVar"),
    ( "DUMMY_VAR23_OR32_THIS", "dummyVar23Or32This"),
]
def test_methods_rename():
    for _in, _out in methods_data:
        assert _out == ConventionNaming.get_method_name(_in)
        assert _out == get_convention_rename(NameType.METHOD, _in)

vars_data = [
    ("Var_2DIY2", "var2Diy2"),
    ("VAR_2diy2", "var2diy2"),
    ("_23dummy$___var23Or32This", "dummyVar23Or32This"),
    ("_23Dummy__23__easy", "dummy23Easy"),
    ("Easier__WHY__$", "easierWhy"),
    ("_23__Simpler___no", "simplerNo"),
    ("_234_Sowhat__$", "sowhat"),
    ("TakeItEasy", "takeItEasy"),
    ("why_i", "whyI"),
    ("__23Yet__234how223Foo_$var______", "yet234how223FooVar"),
    ( "DUMMY_VAR23_OR32_THIS", "dummyVar23Or32This"),
    ("MESSAGE_SIZE", "messageSize"),
    ("PROMPT_CANCEL", "promptCancel")
]
def test_vars_rename():
    for _in, _out in vars_data:
        assert _out == ConventionNaming.get_variable_name(_in)
        assert _out == get_convention_rename(NameType.VARIABLE, _in)

common_data = [
    ("", ""),
    ("__$", ""),
    ("_23$", "")
]
def test_common_data():
    for _in, _out in common_data:
        assert _out == ConventionNaming.get_variable_name(_in)
        assert _out == ConventionNaming.get_class_name(_in)
        assert _out == ConventionNaming.get_annotation_name(_in)
        assert _out == ConventionNaming.get_method_name(_in)
        assert _out == ConventionNaming.get_constant_name(_in)