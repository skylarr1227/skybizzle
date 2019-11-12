def simple_class_factory(**attributes):
    class SimpleClass(object):
        pass

    sc = SimpleClass()
    for name, value in attributes.items():
        setattr(sc, name, value)
    return sc
