Nereid Module
#############


Translation
-----------

Best practice for Nereid Translations is a little bit different from the
usual procedure in Tryton due to the different nature of the
translatable messages in Nereid.
For best results the following workflow is recommended:

- Import translations as usual by installing the module with the desired
  language.

- Run 'Set translations' to import new messages into the database.

- This is the additional step recommended in Nereid:
  Run 'Update translations' just once to get the new translations copied
  to your language *and* updated with the proposal evtl. found on an (old)
  existent string.

- Run 'Clean translations' to remove obsolete messages, that could lead
  to errors in translation mechanism and that are needless to translate.

- Now work on 'Update translations' the second time on a clean set of
  the actual messages. Don't forget to control and unmark fuzzy messages
  that got a proposal from an old string.

- When done, run as usual 'Export translations'.

- Enjoy!

.. note:: When working on translations to be included in the upstream
        package, please work on a clean template tree without
        customizations.


FAQ
---

What are the uses of Nereid?
````````````````````````````

Nereid can be used to build web applications, that could use Tryton's 
ORM as a backend. While there are no inherent limitations which prevent
you from using nereid to build any kind of web application, the design
decision that we made while building nereid itself are tailored to build
applications that extend the functionality of the ERP system, like 
e-commerce system, EDI systems, Customer/Supplier Portals etc.

.. note:: As of version 7.0 the base module for Tryton originally
        contained in this package (nereid) was phased out into a separate 
        package (nereid_base).


Why Tryton as a backend?
````````````````````````

It's scalable, it's flexible and offers a good approach into a declarative coding
pattern for model design in any ORM. The unique way Tryton handles inheritance
also makes it an excellent choice. In addition to the above, Tryton by default
has several modules which make designing business applications faster in 
comparison to other frameworks.

Let's say that you want to build a customer portal, all that you need to do
from your end is create a module which exposes the information that you want to,
and leave other stuff like order management, account management etc to the
existing Tryton modules.

Which version of Tryton does nereid use ?
`````````````````````````````````````````

Nereid being a module for Tryton follows the same versioning of Tryton.

What is the license of Nereid ?
```````````````````````````````

Nereid follows the same license as that of Tryton which is GPLv3.

Is nereid modular ?
```````````````````

Depends on what you think modular is. For us we think Nereid is modular 
because you could separate logically different functionality into a 
separate Tryton module and then the functionality would be available 
to you depending on what modules are installed in the database that you
are accessing.

This also allows modules to be reused. For example, the nereid-catalog
module which makes product information available could just be used for
a display only catalog and is also used as the cart display module for
nereid-webshop - the full eCommerce system.

A little history
````````````````

The initial goal was to build an e-commerce system over OpenERP/Odoo 
called Callisto. It worked, but never scaled on OpenERP. The license
sucked (surprise)! and most issues that were seen with OpenERP
don't exist in Tryton.

