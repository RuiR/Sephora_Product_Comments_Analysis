# Sephora Product Comments Analysis
This project is intended to scrape product information and reviews from sephora.ca for some analysis. It uses selenium to scrape data.

File sephora_scrapping.py is the main file for scrapping products information and reviews. In the script, I used chrome browser. To run 
this code, please download chrome driver to the same directory of sephora_scrapping.py (if you already have Chrome brower). If you prefer 
to use other browser, please also download the browser driver to the same directory of sephora_scrapping.py.

File sephora_scrapping do the following things:
## Get all product names and product link
Given a base link, for example, the base link of all eye cream products in sephora.ca, this part will get product name and product link, and
assign an index for this product as following:

index,product_name,product_link

0,OLEHENRIKSEN Banana Bright Eye Crème,https://www.sephora.com/ca/en/product/banana-bright-eye-creme-P426339?icid2=products%20grid:p426339:product

## Get the general product information 
It could also scrape a product's overall information and overall rate:
1. product_index
2. product_details
3. total_reviews_count
4. number of 5 star rates
5. number of 4 star rates
6. number of 3 star rates
7. number of 2 star rates
8. number of 1 star rates
9. overall rate

## Get information of each review
File sephora_scrapping could scrape the following separate review information:
1. review_user_id
2. review_user_info
3. rate
4. review_date
5. review_content
6. not_helpful
7. helpful

