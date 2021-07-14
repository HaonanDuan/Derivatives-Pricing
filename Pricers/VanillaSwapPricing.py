#!/usr/bin/env python
# coding: utf-8

# In[1]:


import QuantLib as ql


# In[2]:


class PricerBase:
    
    def __init__(self, config):
        self.risk_free_rate = config['risk_free_rate']
        self.libor_rate = config['libor_rate']
        self.calculation_date = config['calculation_date']
        if config['forward'] != None:
            self.forward = int(config['forward'][:-1])
        else:
            self.forward = 0
        self.forward_dt = config['forward'][-1]
        self.maturity = int(config['maturity'][:-1])
        self.fixed_tenor = int(config['fixed_tenor'][:-1])
        self.float_tenor = int(config['float_tenor'][:-1])
        self.maturity_dt = config['maturity'][-1]
        self.fixed_tenor_dt = config['fixed_tenor'][-1]
        self.float_tenor_dt = config['float_tenor'][-1]
    
    def dateType(self, date_type):
        if date_type == 'y':
            return ql.Years
        elif date_type == 'm':
            return ql.Months
        elif date_type == 'd':
            return ql.Days

    def discountCurve(self):
        day_count = ql.Actual365Fixed()
        discount_curve = ql.YieldTermStructureHandle(ql.FlatForward(self.calculation_date, self.risk_free_rate, day_count))
        return discount_curve

    def liborIndex(self):
        day_count = ql.Actual365Fixed()
        libor_curve = ql.YieldTermStructureHandle(ql.FlatForward(self.calculation_date, self.libor_rate, day_count))
        libor_index = ql.Euribor3M(libor_curve)  
        libor_index = ql.USDLibor(ql.Period(self.float_tenor, self.dateType(self.float_tenor_dt)), libor_curve)
        return libor_index

    def fixFloatLegSchedule(self):
        calendar = ql.UnitedKingdom()
        settle_date = calendar.advance(self.calculation_date, self.forward, self.dateType(self.forward_dt))
        maturity_date = calendar.advance(settle_date, self.maturity, self.dateType(self.maturity_dt))
        fixed_leg_tenor = ql.Period(self.fixed_tenor, self.dateType(self.fixed_tenor_dt))
        fixed_schedule = ql.Schedule(settle_date, maturity_date, 
                                    fixed_leg_tenor, calendar,
                                    ql.ModifiedFollowing, ql.ModifiedFollowing,
                                    ql.DateGeneration.Forward, False)
        float_leg_tenor = ql.Period(self.float_tenor, self.dateType(self.float_tenor_dt))
        float_schedule = ql.Schedule (settle_date, maturity_date, 
                                    float_leg_tenor, calendar,
                                    ql.ModifiedFollowing, ql.ModifiedFollowing,
                                    ql.DateGeneration.Forward, False)
        return fixed_schedule, float_schedule

    def price(self, notional, fixed_rate, float_spread):
        return 0


# In[3]:


class VanillaSwap(PricerBase):

    def __init__(self, config):
        super().__init__(config)

    def Pricer(self, config):
        notional = config['notional']
        fixed_rate = config['fixed_rate']
        float_spread = config['float_spread']
        fixed_leg_daycount = ql.Actual365Fixed()
        float_leg_daycount = ql.Actual365Fixed()
        discount_curve = self.discountCurve()
        libor_index = self.liborIndex()
        fixed_schedule, float_schedule = self.fixFloatLegSchedule()
        ir_swap = ql.VanillaSwap(ql.VanillaSwap.Payer, notional, fixed_schedule, 
                    fixed_rate, fixed_leg_daycount, float_schedule,
                    libor_index, float_spread, float_leg_daycount )
        swap_engine = ql.DiscountingSwapEngine(discount_curve)
        
        ir_swap.setPricingEngine(swap_engine)
        return ir_swap


# In[6]:


if __name__ == '__main__':
    my_config = {'risk_free_rate':0.01,'libor_rate':0.02,'calculation_date':ql.Date(31, 12, 2021),'forward':'5d','maturity':'10y',
            'fixed_tenor':'6m','float_tenor':'3m','notional':10e6,'fixed_rate':0.025,'float_spread':0.004}
    vanilla = VanillaSwap(my_config)
    price = vanilla.Pricer(my_config)
    print("Fixed Leg Cashflows:")
    for i, cf in enumerate(price.leg(0)):
        print("%2d    %-18s  %10.2f"%(i+1, cf.date(), cf.amount()))
    print("\nFloating Leg Cashflows:")
    for i, cf in enumerate(price.leg(1)):
        print(i+1, cf.date(), cf.amount())

