from .invoice import generate

"""
    It's best practice to have '__init__.py' under a package cause it makes importing functions and classes easier. 
    Easy as in we don't have to mention the sub-package, module name to import a function.
    For ex:
        from invoicing.invoice import generate
        
    Instead of importing like demonstrated above we can import like this 'from invoicing import generate' 
    This is only possible with the '__init__.py' and this 1st line in it.
"""