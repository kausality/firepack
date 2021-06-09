from firepack.service import FireService
from firepack.fields import ListField, CharField


class Service(FireService):
    a = ListField(ListField(ListField(CharField())))

    def fire(self, **kwargs):
        print(self.a)


s = Service()
s.call({
    'a': [[['a', 'b'], ['c', 'd']], [['e', 'f'], ['g', 'h']]]
})
