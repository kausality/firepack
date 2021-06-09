from firepack.fields import Field
from firepack.errors import ValidationError, MultiValidationError, ParamError, SkipError, ModificationError


class FireService:
    """Class which manages the execution of Services. You should subclass this to have managed Service execution.

    Example:
    
    ```python
    class SendWelcomeEmail(FireService):
        name = StrField()
        email = EmailField()

        def pre_fire(self):
            if not connection_up():
                raise SkipError('Connection is down!')

        def fire(self):
            send_welcome_email(self.name, self.email, 'Hello %s, we are happy to see you back on Endurance!' % name)

        def post_fire(self, fired, exc):
            if fired:
                log_email_success(self.name, self.email)
            else:
                log_email_failure(self.name, self.email, exc)

    SendWelcomeEmail.call({
        'name': 'Murphy Cooper',
        'email': 'murphy@example.com'
    })
    ```
    """
    _MOD_TABLE_ = '_MOD_TABLE'

    def __setattr__(self, name, value):
        is_field_attr = (name in type(self).__dict__) and isinstance(type(self).__dict__[name], Field)
        if self.__dict__[self._MOD_TABLE_].get(name) and is_field_attr:
            raise ModificationError('Attempt to change field: %s' % name)
        val = super().__setattr__(name, value)
        self.__dict__[self._MOD_TABLE_][name] = True
        return val

    def call(self, input_dict, exact=True, **kwargs):
        """This method should be called to start the execution of the Service.

        Args:
            input_dict (dict): Dictionary of input values which maps to `Field` properties in `FireService` class.
            exact (bool, optional): If set to `True`, any key in `input_dict` which doesn't maps to any declared `Field` properties in the Service class will raise `ParamError`. Defaults to True.

        Returns:
            object: Return value of `fire()` method.

        Raises:
            ParamError: Raised when any key in `input_dict` doesn't matches one of the declared `Field` properties and `exact` is set to `True`.
            MultiValidationError: Raised when `Field` values contains validation errors.
        """

        assert isinstance(input_dict, dict), 'input_dict should be of type dict'

        # Each invocation of call resets the modification table
        self.__dict__[self._MOD_TABLE_] = dict()
        self._process_input(input_dict, exact)
        call_fire = True
        exc = None
        return_value = None
        try:
            self.pre_fire()
        except SkipError as ex:
            call_fire = False
            exc = ex
        if call_fire:
            return_value = self.fire(**kwargs)
        self.post_fire(call_fire, exc)
        return return_value

    def _process_input(self, input_dict, exact):
        # Get all Field descriptors in subclass
        fields = self._get_fields(type(self))

        field_names = [name for name, _ in fields]
        # Validate that input doesn't contains any key which doesn't exist in FireService Field's definition
        for key in input_dict.keys():
            if key not in field_names and exact:
                raise ParamError(key)

        errors = []
        for name, desc_obj in fields:
            value = input_dict.get(name)
            # Make it an instance field so it can be accessed as normal python object properties
            setattr(self, name, value)
            try:
                desc_obj._run_validation(value)
            except ValidationError as ex:
                errors.append(ex)
            except SkipError:
                pass

        if errors:
            raise MultiValidationError(errors)

    @staticmethod
    def _get_fields(subclass):
        return [(name, desc_obj) for name, desc_obj in subclass.__dict__.items() if isinstance(desc_obj, Field)]

    def pre_fire(self):
        """Method called before the execution of Service, that is, called before the `fire()` method.
        Raise `SkipError` here to prevent the execution of `fire()`.
 
        Raises:
            SkipError: Raising this exception prevents the execution of `fire()` method. Usually used to prevent service execution based on some conditions.
        """
        pass

    def fire(self, **kwargs):
        """The entry point of your Service. This method should be implemented in your Service.
        
        Raises:
            NotImplementedError: Raised if subclass does not implement this method.
        """
        raise NotImplementedError

    def post_fire(self, fired, exc):
        """Called after execution of `fire()` and also called if `fire()` execution was skipped in `pre_fire()`
        Mostly used to perform cleanup or logging operations post Service execution.

        Note: This method is never called if their was an error other than `SkipError`.
        
        Args:
            fired (bool): Flag indicating if `fire()` method was executed.
            exc (SkipError): Contains any exception raised in `pre_fire()` or `fire()` methods otherwise None.
        """
        pass
