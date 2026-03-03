import pytest

def test_product_validation():
    with pytest.raises(ValueError):
        Product("SKU1", "Test", "cat", -10, 0.23, 1)

def test_minimum_price():
    p = Product("SKU1", "Test", "cat", 10, 0.23, 1)
    p.apply_discount(15)
    assert p.discounted_price == 1.0

def test_category_percentage_promotion():
    p = Product("SKU1", "Test", "books", 100, 0.05, 1)
    c = Cart([p])
    promo = CategoryPercentagePromotion("books", 0.15)
    promo.apply(c)
    assert p.discounted_price == 85.0

def test_outlet_no_percentage_promotion():
    p = Product("SKU1", "Test", "outlet", 100, 0.23, 1)
    c = Cart([p])
    promo = CategoryPercentagePromotion("outlet", 0.15)
    promo.apply(c)
    assert p.discounted_price == 100.0

def test_two_plus_one_promotion():
    p = Product("SKU1", "Test", "cat", 100, 0.23, 3)
    c = Cart([p])
    promo = TwoPlusOnePromotion(["SKU1"])
    promo.apply(c)
    assert round(p.discounted_price, 2) == 66.67

def test_two_plus_one_qty_4():
    p = Product("SKU1", "Test", "cat", 100, 0.23, 4)
    c = Cart([p])
    promo = TwoPlusOnePromotion(["SKU1"])
    promo.apply(c)
    assert p.discounted_price == 75.0

def test_coupon_promotion():
    p = Product("SKU1", "Test", "cat", 100, 0.23, 1)
    c = Cart([p])
    promo = FixedAmountCouponPromotion(20, 50)
    promo.apply(c)
    assert p.discounted_price == 80.0

def test_coupon_not_applied_if_below_threshold():
    p = Product("SKU1", "Test", "cat", 40, 0.23, 1)
    c = Cart([p])
    promo = FixedAmountCouponPromotion(20, 50)
    promo.apply(c)
    assert p.discounted_price == 40.0

def test_coupon_and_two_plus_one_exclusion():
    p = Product("SKU1", "Test", "cat", 100, 0.23, 3)
    c = Cart([p])
    promos = [TwoPlusOnePromotion(["SKU1"]), FixedAmountCouponPromotion(50, 100)]
    engine = PromotionEngine(promos)
    engine.apply_promotions(c)
    assert round(p.discounted_price, 2) == 66.67

def test_free_shipping():
    p = Product("SKU1", "Test", "cat", 250, 0.23, 1)
    c = Cart([p])
    promo = FreeShippingPromotion(200, 15)
    assert promo.apply(c) == 15

def test_cheapest_half_price():
    p1 = Product("SKU1", "Test1", "cat", 100, 0.23, 1)
    p2 = Product("SKU2", "Test2", "cat", 50, 0.23, 1)
    c = Cart([p1, p2])
    promo = CheapestProductHalfPricePromotion("cat")
    promo.apply(c)
    assert p1.discounted_price == 100.0
    assert p2.discounted_price == 25.0

def test_receipt_generation():
    p = Product("SKU1", "Test", "cat", 100, 0.23, 1)
    c = Cart([p])
    promos = [FixedAmountCouponPromotion(20, 50)]
    engine = PromotionEngine(promos)
    engine.apply_promotions(c)
    receipt = Receipt(c, 15, 0)
    data = receipt.generate()
    assert data["summary"]["total_gross"] == 95.0
    assert data["summary"]["total_savings"] == 20.0