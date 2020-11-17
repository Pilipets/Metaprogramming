from src.core.convention.convention_naming import get_convention_rename, ConventionNaming, NameType

const_vars_data = [
    ("_23dummy$___var23Or32This", "DUMMY_VAR23_OR32_THIS"),
    ("_23Dummy__23__easy", "DUMMY_23_EASY"),
    ("EasierWhy__$", "EASIER_WHY"),
    ("_23__Simpler___no", "SIMPLER_NO"),
    ("_234_Sowhat__$", "SOWHAT"),
    ("TakeItEasy", "TAKE_IT_EASY"),
    ("why_i", "WHY_I"),
    ("__23Yet__234how223Foo_$var______", "YET_234HOW223_FOO_VAR"),
    ("", ""),
    ("__$", ""),
    ("_23$", "")
]
def test_const_vars_rename():
    for _in, _out in const_vars_data:
        assert _out == ConventionNaming.get_constant_name(_in)
        assert _out == get_convention_rename(NameType.CONST_VARIABLE, _in)


class_vars_data = [
    ("Var_2DIY2", "Var2diy2"),
    ("VAR_2diy2", "Var2diy2"),
    ("_23dummy$___var23Or32This", "DummyVar23Or32This"),
    ("_23Dummy__23__easy", "Dummy23Easy"),
    ("Easier__WHY__$", "EasierWhy"),
    ("_23__Simpler___no", "SimplerNo"),
    ("_234_Sowhat__$", "Sowhat"),
    ("SOWHAT", "Sowhat"),
    ("TakeItEasy", "TakeItEasy"),
    ("why_i", "WhyI"),
    ("__23Yet__234how223Foo_$var______", "Yet234how223FooVar"),
    ("", ""),
    ("__$", ""),
    ("_23$", "")
]
def test_class_vars_rename():
    for _in, _out in class_vars_data:
        assert _out == ConventionNaming.get_class_name(_in)
        assert _out == get_convention_rename(NameType.CLASS, _in)


methods_vars_data = [
    ("Var_2DIY2", "var2diy2"),
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
    ("", ""),
    ("__$", ""),
    ("_23$", "")
]
def test_method_vars_rename():
    for _in, _out in class_vars_data:
        assert _out == ConventionNaming.get_method_name(_in)
        assert _out == get_convention_rename(NameType.METHOD, _in)
        assert _out == ConventionNaming.get_variable_name(_in)
        assert _out == get_convention_rename(NameType.VARIABLE, _in)

if __name__ == '__main__':
    test_const_vars_rename()
    test_class_vars_rename()
