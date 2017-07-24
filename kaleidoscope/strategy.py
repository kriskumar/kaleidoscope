import datetime
from kaleidoscope.globals import OrderType
from kaleidoscope.event import OrderEvent
from kaleidoscope.sizers.sizers import FixedQuantitySizer
from kaleidoscope.order import Order


class Strategy(object):
    """
    This is the base class that holds various functions that implement custom trading
    logic such as entry/exit strategies and other trading mechanics
    based on option greeks and prices.
    """

    def __init__(self, broker, account, queue, **params):
        self.broker = broker
        self.account = account

        self.queue = queue

        self.start_date = None
        self.end_date = None

        if 'sizer' not in params:
            self.sizer = FixedQuantitySizer(self.account)

        self._init(**params)

    def set_cash(self, amt):
        """
        Set the cash balance of brokerage account

        :param amt: The cash amount to set for the trading account
        :return:
        """
        self.account.set_cash(amt)

    def add_option(self, symbol, exclude_splits=True, option_type=None):
        """
        Pass the parameters and option strategy to create to the broker

        :param symbol: symbol to add option for
        :param exclude_splits: exclude options created from the underlying's stock splits
        :param option_type: If None, or not passed in, will retrieve both calls and puts of option chain
        :return: None
        """
        self.broker.source(symbol, self.start_date, self.end_date, exclude_splits, option_type)

    def set_start_date(self, year, month, day):
        """
        Set start date of backtest

        :param year: year of start date
        :param month: month of start date
        :param day: day of start date
        :return:
        """
        self.start_date = datetime.date(year=year, month=month, day=day).strftime("%Y-%m-%d")

    def set_end_date(self, year, month, day):
        """
        Set end date of backtest

        :param year: year of end date
        :param month: month of end date
        :param day: day of end date
        :return:
        """

        self.end_date = datetime.date(year=year, month=month, day=day).strftime("%Y-%m-%d")

    def _init(self, **params):
        """
        Perform any strategy class specific initialization logic here, then
        initialize the actual custom strategy class.

        :param params: params to be passed into custom strategy
        :return:
        """

        # register strategy params as instance class attributes
        self.__dict__.update(params)

        self.on_init(**params)

    def on_init(self, **params):
        raise NotImplementedError

    def on_data(self, data):
        raise NotImplementedError

    def on_fill(self, event):
        pass

    def stop(self):
        pass

    def buy(self, order, order_type=OrderType.MKT, quantity=None):
        """
        Create a buy signal event and place it in the queue

        :param order:
        :param order_type:
        :param quantity:
        :return:
        """
        if quantity <= 0:
            raise ValueError("Quantity cannot be less than 1")
        elif quantity is None:
            # use sizer to determine quantity
            quantity = self.sizer.order_size(self.account, order)

        # create an new order and place it in the queue
        # order = Order(order)
        event = OrderEvent(Order(options, order_type, quantity))

        self.queue.put(event)

    def sell(self, options, order_type=OrderType.MKT, quantity=None):
        """
        Create a sell order event and place it in the queue
        :param options:
        :param order_type:
        :param quantity:
        :return:
        """
        pass

    def close(self):
        pass

    def cancel(self):
        pass