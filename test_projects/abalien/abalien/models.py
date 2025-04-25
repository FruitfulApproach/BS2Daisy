from neomodel import StructuredNode, IntegerProperty


class MyNode(StructuredNode):
    my_prop = IntegerProperty()
        
    class Meta:
        app_label = "myapp"    