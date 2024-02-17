# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from decimal import Decimal

from trytond.exceptions import UserError
from trytond.modules.account.tests import create_chart, get_fiscalyear
from trytond.modules.company.tests import (
    CompanyTestMixin, create_company, set_company)
from trytond.modules.currency.tests import add_currency_rate, create_currency
from trytond.pool import Pool
from trytond.tests.test_tryton import ModuleTestCase
from trytond.tests.test_tryton import with_transaction
from trytond.transaction import Transaction

try:
    from trytond.modules.account_invoice.tests import set_invoice_sequences
except:
    set_invoice_sequences = None


def create_payment_term():
    pool = Pool()
    PaymentTerm = pool.get('account.invoice.payment_term')

    return PaymentTerm.create([{
        'name': 'Direct',
        'lines': [('create', [{'type': 'remainder'}])]
        }])[0]


def setup_fiscalyear():
    pool = Pool()
    Company = pool.get('company.company')
    FiscalYear = pool.get('account.fiscalyear')
    Account = pool.get('account.account')

    companies = Company.search([])
    if companies:
        company = companies[0]
    else:
        company = create_company()

    with set_company(company):
        try:
            fiscalyear = FiscalYear.find(company.id, test_state=True)
        except:
            fiscalyear = get_fiscalyear(company)
        # Set the invoice sequences if account_invoice is installed
        if set_invoice_sequences:
            fiscalyear = set_invoice_sequences(fiscalyear)
        fiscalyear.save()
        if not fiscalyear.periods:
            FiscalYear.create_period([fiscalyear])
        if not Account.search([], limit=1):
            create_chart(company)


def setup_users():
    pool = Pool()
    Company = pool.get('company.company')
    User = pool.get('res.user')
    Model = Pool().get('ir.model.data')

    # Setup users
    sales_users = User.search([
                ('login', '=', 'sale'),
                ])
    if not sales_users:
        company, = Company.search([])
        group_sale_admin_id = Model.get_id('sale', 'group_sale_admin')
        group_sale_id = Model.get_id('sale', 'group_sale')

        with set_company(company):
            basic_user, = User.create([{
                        'name': 'Basic User',
                        'login': 'basic',
                        'company': company,
                        }])
            sales_user, = User.create([{
                        'name': 'Sales Person',
                        'login': 'sale',
                        'company': company,
                        'groups': [('add', [
                                    group_sale_id,
                                    ])]
                        }])
            sales_admin, = User.create([{
                        'name': 'Sales Admin',
                        'login': 'sale_admin',
                        'company': company,
                        'groups': [('add', [
                                    group_sale_admin_id,
                                ])]
                        }])
    else:
        sales_user = sales_users[0]
        basic_user, = User.search([
                    ('login', '=', 'basic'),
                    ])
        sales_admin, = User.search([
                    ('login', '=', 'sale_admin'),
                    ])
    users = {
        'basic_user': basic_user,
        'sales_user': sales_user,
        'sales_admin': sales_admin,
        }
    return users


def create_sale(amount=Decimal('200')):
    """
    Create test sale with provided amount
    """
    pool = Pool()
    Currency = pool.get('currency.currency')
    Party = pool.get('party.party')
    Company = pool.get('company.company')
    Sale = pool.get('sale.sale')
    Account = pool.get('account.account')
    Journal = pool.get('account.journal')

    payment_term = create_payment_term()

    currencies = Currency.search([
            ('code', '=', 'USD'),
            ])
    if currencies:
        currency = currencies[0]
    else:
        currency = create_currency('USD')
        try:
            add_currency_rate(currency, Decimal('1'))
        except:
            pass

    company, = Company.search([])
    with set_company(company):
        journal_revenue, = Journal.search([
                ('code', '=', 'REV'),
                ])
        journal_expense, = Journal.search([
                ('code', '=', 'EXP'),
                ])
        journal_cash, = Journal.search([
                ('code', '=', 'CASH'),
                ])
        revenue, = Account.search([
                ('type.revenue', '=', True),
                ])
        receivable, = Account.search([
                ('type.receivable', '=', True),
                ])

        with Transaction().set_context(company=company.id):
            party, = Party.create([{
                        'name': 'Bruce Wayne',
                        'addresses': [('create', [{
                                        'name': 'Bruce Wayne',
                                        'city': 'Gotham',
                                        }])],
                        'customer_payment_term': payment_term,
                        'account_receivable': receivable,
                        'contact_mechanisms': [('create', [
                                    {'type': 'mobile', 'value': '8888888888'},
                                    ])],
                        }])

            sale, = Sale.create([{
                        'reference': 'Test Sale',
                        'payment_term': payment_term,
                        'currency': currency,
                        'party': party.id,
                        'invoice_address': party.addresses[0].id,
                        'shipment_address': party.addresses[0].id,
                        'company': company.id,
                        'invoice_method': 'manual',
                        'shipment_method': 'manual',
                        'lines': [('create', [{
                                        'description': 'Some item',
                                        'unit_price': amount,
                                        'quantity': 1,
                                        }])]
                        }])
    return sale


def create_channel_sale(user=None, channel=None):
    pool = Pool()
    Company = pool.get('company.company')
    SaleChannel = pool.get('sale.channel')

    # Create the channels
    company, = Company.search([])
    users = setup_users()
    if not SaleChannel.search([]):
        create_sale_channels(company)

    if not user:
        users = setup_users()
        user = users['basic_user']
    with Transaction().set_user(user.id) as u, Transaction().set_context(
            company=company.id,
            current_channel=channel,
            language='en') as c:
                channel_sale = create_sale()
                channel_sale.save()
                channel_sale.on_change_channel()
    return channel_sale


def create_sale_channels(company):
    pool = Pool()
    Location = pool.get('stock.location')
    SaleChannel = pool.get('sale.channel')
    PriceList = pool.get('product.price_list')

    with Transaction().set_context(company=company.id):
        price_list = PriceList(
            name='PL 1',
            company=company
            )
        price_list.save()

        address = company.party.addresses[0]
        warehouse, = Location.search([
                ('code', '=', 'WH')
                ])
        setup_users()
        payment_term = create_payment_term()

        channel1, channel2, channel3, channel4 = \
            SaleChannel.create([{
                'name': 'Channel 1',
                'code': 'C1',
                'address': address,
                'source': 'manual',
                'timezone': 'UTC',
                'warehouse': warehouse,
                'invoice_method': 'manual',
                'shipment_method': 'manual',
                'payment_term': payment_term.id,
                'price_list': price_list,
            }, {
                'name': 'Channel 2',
                'code': 'C2',
                'address': address,
                'source': 'manual',
                'timezone': 'US/Pacific',
                'warehouse': warehouse,
                'invoice_method': 'manual',
                'shipment_method': 'manual',
                'payment_term': payment_term.id,
            }, {
                'name': 'Channel 3',
                'code': 'C3',
                'address': address,
                'source': 'manual',
                'warehouse': warehouse,
                'invoice_method': 'manual',
                'shipment_method': 'manual',
                'payment_term': payment_term.id,
            }, {
                'name': 'Channel 4',
                'code': 'C4',
                'address': address,
                'source': 'manual',
                'timezone': 'US/Eastern',
                'warehouse': warehouse,
                'invoice_method': 'manual',
                'shipment_method': 'manual',
                'payment_term': payment_term.id,
            }])


def create_product(name, vlist, uri, uom='Unit'):
    """
    Create a product template with products and return its ID
    :param name: Name of the product
    :param vlist: List of dictionaries of values to create
    :param uri: uri of product template
    :param uom: Note it is the name of UOM (not symbol or code)
    """
    pool = Pool()
    Company = pool.get('company.company')
    ProductTemplate = pool.get('product.template')
    Uom = pool.get('product.uom')

    company, = Company.search([])
    with set_company(company), Transaction().set_context(company=company.id):
        uom, = Uom.search([('name', '=', uom)], limit=1)
        for values in vlist:
            values['name'] = name
            values['default_uom'] = uom
            values['sale_uom'] = uom
            values['products'] = [('create', [{}])]
        product, = ProductTemplate.create(vlist)
    return product


class SaleChannelPriceListTestCase(CompanyTestMixin, ModuleTestCase):
    'Test Sale Channel Price List module'
    module = 'sale_channel_price_list'

    @with_transaction()
    def test_0005_channel_status_bar(self):
        pool = Pool()
        Company = pool.get('company.company')
        SaleChannel = pool.get('sale.channel')

        # Setup defaults
        setup_fiscalyear()

        users = setup_users()
        sales_user = users['sales_user']
        company, = Company.search([])
        create_sale_channels(company)

        channel1, channel2, channel3, channel4 = SaleChannel.search(
            [], order=[('code', 'ASC')])

        sales_user.current_channel = channel3
        sales_user.save()

        self.assertTrue(channel3.name in sales_user.status_bar)

    @with_transaction()
    def test_0010_channel_required(self):
        pool = Pool()
        Company = pool.get('company.company')
        SaleChannel = pool.get('sale.channel')

        # Setup defaults
        setup_fiscalyear()

        users = setup_users()
        sales_admin = users['sales_admin']
        company, = Company.search([])
        create_sale_channels(company)

        channel1, channel2, channel3, channel4 = SaleChannel.search(
            [], order=[('code', 'ASC')])

        # Test the custom UserError:
        # First go to user preferences and select a current_channel for "%s".
        with self.assertRaises(UserError):
            sale = create_channel_sale(sales_admin, channel=None)

    @with_transaction()
    def test_0050_check_duplicate_channel_identifier_for_sale(self):
        """
        Check if error is raised for duplicate channel identifier in sale
        """
        pool = Pool()
        Company = pool.get('company.company')
        SaleChannel = pool.get('sale.channel')

        # Setup defaults
        setup_fiscalyear()

        users = setup_users()
        sales_user = users['sales_user']
        company, = Company.search([])
        create_sale_channels(company)

        channel1, channel2, channel3, channel4 = SaleChannel.search(
            [], order=[('code', 'ASC')])

        sales_user.current_channel = channel3
        sales_user.save()
        sale1 = create_channel_sale(user=sales_user,
            channel=channel3.id)
        sale2 = create_channel_sale(user=sales_user,
            channel=channel3.id)

        sale1.channel_identifier = 'Test Sale 1'
        sale1.save()

        # Same channel identifier for sale 2 should raise error
        with self.assertRaises(UserError):
            sale2.channel_identifier = 'Test Sale 1'
            sale2.save()

    @with_transaction()
    def test_0060_return_sale_with_channel_identifier(self):
        """
        Check if return sale works with channel_identifier
        """
        pool = Pool()
        Company = pool.get('company.company')
        Sale = pool.get('sale.sale')
        SaleChannel = pool.get('sale.channel')
        ReturnSale = pool.get('sale.return_sale', type='wizard')

        # Setup defaults
        setup_fiscalyear()

        users = setup_users()
        sales_user = users['sales_user']
        company, = Company.search([])
        create_sale_channels(company)

        channel1, channel2, channel3, channel4 = SaleChannel.search(
            [], order=[('code', 'ASC')])

        sales_user.current_channel = channel3
        sales_user.save()
        sale1 = create_channel_sale(user=sales_user,
            channel=channel3.id)
        sale2 = create_channel_sale(user=sales_user,
            channel=channel3.id)

        sale1.channel_identifier = 'Test Sale 1'
        sale1.save()

        with Transaction().set_user(sales_user.id):
            # Return sale with channel identifier
            session_id, _, _ = ReturnSale.create()
            return_sale = ReturnSale(session_id)
            with Transaction().set_context(
                    active_model='sale.sale',
                    active_id=sale1.id,
                    company=company.id):
                return_sale.do_return_(return_sale.return_.get_action())

            # Return a sale with lines
            sale2.channel_identifier = 'Test Sale 2'
            sale2.save()
            Sale.write([sale2], {
                'lines': [
                    ('create', [{
                        'type': 'comment',
                        'channel_identifier': 'Test Sale Line',
                        'description': 'Test Desc'
                    }])
                ]
            })

            session_id, _, _ = ReturnSale.create()
            return_sale = ReturnSale(session_id)
            with Transaction().set_context(
                    active_model='sale.sale',
                    active_id=sale2.id,
                    company=company.id):
                return_sale.do_return_(return_sale.return_.get_action())

    @with_transaction()
    def test_0080_map_tax(self):
        """
        Check if tax is mapped
        """
        pool = Pool()
        Company = pool.get('company.company')
        SaleChannel = pool.get('sale.channel')
        SaleChannelTax = pool.get('sale.channel.tax')
        Tax = pool.get('account.tax')
        Account = pool.get('account.account')

        # Setup defaults
        setup_fiscalyear()

        company, = Company.search([])
        create_sale_channels(company)

        channel1, channel2, channel3, channel4 = SaleChannel.search(
            [], order=[('code', 'ASC')])

        with set_company(company):
            cash, = Account.search([
                    ('type.receivable', '=', True),
                    ('type.statement', '=', 'balance'),
                    ])
            tax1, = Tax.create([
                {
                    'name': "tax1",
                    'description': "Tax description",
                    'type': 'percentage',
                    'company': company.id,
                    'invoice_account': cash,
                    'credit_note_account': cash,
                    'rate': Decimal('8.00'),
                }
            ])

        mapped_tax, = SaleChannelTax.create([{
            'name': 'new_channel_tax',
            'rate': Decimal('8.00'),
            'tax': tax1.id,
            'channel': channel1.id,
            }])

        self.assertEqual(
            channel1.get_tax('new_channel_tax', Decimal('8.00')), tax1)

    @with_transaction()
    def test_0100_check_channel_exception(self):
        """
        Check if channel exception is being created
        """
        pool = Pool()
        Company = pool.get('company.company')
        SaleChannel = pool.get('sale.channel')
        ChannelException = pool.get('channel.exception')

        # Setup defaults
        setup_fiscalyear()

        users = setup_users()
        sales_user = users['sales_user']
        company, = Company.search([])
        create_sale_channels(company)

        channel1, channel2, channel3, channel4 = SaleChannel.search(
            [], order=[('code', 'ASC')])

        sales_user.current_channel = channel3
        sales_user.save()
        sale = create_channel_sale(user=sales_user,
            channel=channel3.id)
        self.assertEqual(sale.invoice_method, 'manual')
        self.assertEqual(sale.channel_type, channel3.source)

        self.assertFalse(sale.has_channel_exception)

        channel_exception, = ChannelException.create([{
            'origin': '%s,%s' % (sale.__name__, sale.id),
            'log': 'Sale has exception',
            'channel': sale.channel.id,
            }])

        self.assertTrue(channel_exception)
        self.assertTrue(sale.has_channel_exception)

        # Mark exception as resolved
        channel_exception.is_resolved = True
        channel_exception.save()

        self.assertFalse(sale.has_channel_exception)

    #@with_transaction()
    #def test_0110_check_channel_exception_searcher(self):
    #    """
    #    Check searcher for channel exception
    #    """
    #    pool = Pool()
    #    Company = pool.get('company.company')
    #    Sale = pool.get('sale.sale')
    #    SaleChannel = pool.get('sale.channel')
    #    ChannelException = pool.get('channel.exception')

    #    # Setup defaults
    #    # A gateway sets up a lot of configuration stuff (fiscalyear, chart,
    #    # etc.)
    #    setup_fiscalyear()

    #    users = setup_users()
    #    sales_user = users['sales_user']
    #    company, = Company.search([])
    #    create_sale_channels(company)

    #    channel1, channel2, channel3, channel4 = SaleChannel.search(
    #        [], order=[('code', 'ASC')])

    #    sales_user.current_channel = channel3
    #    sales_user.save()
    #    sale1 = create_channel_sale(user=sales_user,
    #        channel=channel3.id)
    #    sale2 = create_channel_sale(user=sales_user,
    #        channel=channel3.id)
    #    sale3 = create_channel_sale(user=sales_user,
    #        channel=channel3.id)

    #    self.assertFalse(sale1.has_channel_exception)
    #    self.assertFalse(sale2.has_channel_exception)

    #    self.assertEqual(Sale.search([
    #                ('has_channel_exception', '=', True),
    #                ], count=True), 0)
    #    self.assertEqual(Sale.search([
    #                ('has_channel_exception', '=', False),
    #                ], count=True), 3)

    #    ChannelException.create([{
    #                'origin': '%s,%s' % (sale1.__name__, sale1.id),
    #                'log': 'Sale has exception',
    #                'channel': sale1.channel.id,
    #                'is_resolved': False,
    #                }])

    #    ChannelException.create([{
    #                'origin': '%s,%s' % (sale2.__name__, sale2.id),
    #                'log': 'Sale has exception',
    #                'channel': sale2.channel.id,
    #                'is_resolved': True,
    #                }])

    #    self.assertEqual(Sale.search([('has_channel_exception', '=', True)]),
    #        [sale1])

    #    # Sale2 has exception but is resolved already
    #    self.assertEqual(Sale.search([('has_channel_exception', '=', False)]),
    #        [sale3, sale2])

    @with_transaction()
    def test_0200_orders_import_wizard(self):
        """
        Check orders import wizard
        """
        pool = Pool()
        Company = pool.get('company.company')
        SaleChannel = pool.get('sale.channel')
        Account = pool.get('account.account')
        AccountConfiguration = pool.get('account.configuration')
        ImportDataWizard = pool.get('sale.channel.import_data', type='wizard')

        # Setup defaults
        setup_fiscalyear()

        company, = Company.search([])
        create_sale_channels(company)

        channel1, channel2, channel3, channel4 = SaleChannel.search(
            [], order=[('code', 'ASC')])

        with Transaction().set_context(
                active_model='sale.channel',
                active_id=channel1.id,
                company=company.id):
            session_id, start_state, end_state = ImportDataWizard.create()
            ImportDataWizard.execute(session_id, {}, start_state)
            import_data = ImportDataWizard(session_id)
            import_data.start.import_orders = True
            import_data.start.import_products = True
            import_data.start.channel = channel1

            # Unset default accounts already set by inherited test routines
            configuration = AccountConfiguration(1)
            configuration.default_category_account_expense = None
            configuration.default_category_account_revenue = None
            configuration.save()
            # Product / Order is being imported but default accounts are not
            # set. So it will ask for accounts first
            self.assertFalse(import_data.get_default_account('revenue'))
            self.assertFalse(import_data.get_default_account('expense'))

            self.assertEqual(import_data.transition_next(), 'choose_accounts')

            with set_company(company):
                revenue, = Account.search([
                        ('type.revenue', '=', True),
                        ])
                expense, = Account.search([
                        ('type.expense', '=', True),
                        ])

            # Configure default accounts
            configuration.default_category_account_expense = expense
            configuration.default_category_account_revenue = revenue
            configuration.save()
            self.assertTrue(import_data.get_default_account('revenue'))
            self.assertTrue(import_data.get_default_account('expense'))

            # Since default accounts are set, it wont ask for choose_accounts
            # again
            self.assertEqual(import_data.transition_next(), 'import_')

            with self.assertRaises(NotImplementedError):
                # NotImplementedError is thrown in this case.
                # Importing orders feature is not available in this module
                import_data.transition_import_()

    @with_transaction()
    def test_0210_channel_availability(self):
        pool = Pool()
        StockMove = pool.get('stock.move')
        Location = pool.get('stock.location')
        SaleChannel = pool.get('sale.channel')
        Company = pool.get('company.company')

        # Setup defaults
        setup_fiscalyear()

        company, = Company.search([])
        create_sale_channels(company)

        channel1, channel2, channel3, channel4 = SaleChannel.search(
            [], order=[('code', 'ASC')])

        # Create product templates with products
        template1 = create_product(
            'product-1',
            [{
                'type': 'goods',
                'salable': True,
                'list_price': Decimal('10'),
            }],
            uri='product-1',
        )
        template2 = create_product(
            'product-2',
            [{
                'type': 'goods',
                'salable': True,
                'list_price': Decimal('15'),
            }],
            uri='product-2',
        )

        product1 = template1.products[0]
        product2 = template2.products[0]

        self.assertEqual(
            channel1.get_availability(product1),
            {'type': 'bucket', 'value': 'out_of_stock'}
            )
        self.assertEqual(
            channel1.get_availability(product2),
            {'type': 'bucket', 'value': 'out_of_stock'}
            )

        lost_and_found, = Location.search([
            ('type', '=', 'lost_found')
            ])
        with Transaction().set_context(company=company.id):
            # Bring in inventory for item 1
            moves = StockMove.create([{
                'from_location': lost_and_found,
                'to_location': channel1.warehouse.storage_location,
                'quantity': 10,
                'product': product1,
                'unit': product1.default_uom,
                }])
            StockMove.do(moves)
        self.assertEqual(
            channel1.get_availability(product1),
            {'type': 'bucket', 'value': 'in_stock'}
            )
        self.assertEqual(
            channel1.get_availability(product2),
            {'type': 'bucket', 'value': 'out_of_stock'}
            )

        # Test on channel without price_list
        self.assertEqual(
            channel2.get_availability(product1),
            {'type': 'bucket', 'value': 'in_stock'}
            )
        self.assertEqual(
            channel2.get_availability(product2),
            {'type': 'bucket', 'value': 'out_of_stock'}
            )


del ModuleTestCase
