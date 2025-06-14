This project was created to serve two purposes:

-Create a sitemap of a chosen URL and all of its subpages and output to excel and .pkl file
-Detect 404 links within a URL and all of its subpages and record which page the crawler was on when it attempted to visit the 404 link (for easier tracing and fixing of 404's)

**Use cases include:**

-Crawl a site and store the results:  
 python crawler.py --crawl https://example.com

-Visualize from a stored graph:  
 python crawler.py --map

-Export to Excel from a stored graph:  
 python crawler.py --excel

-Do everything:  
 python crawler.py --crawl https://example.com --map --excel  

-Stop at first 404 error found:  
 python crawler.py --crawl https://example.com --debug-stop-on-404

**Features include:**

-Crawls paginated sections
-Produces a .pkl sitemap  
-Produces an excel spreadsheet sitemap

Example 404 output:

![image](https://github.com/user-attachments/assets/efc82f14-7fa7-492b-b69b-434476d42567)

Example excel spreadhseet sitemap:

![image](https://github.com/user-attachments/assets/34523798-bccf-493b-aad9-b8641312b025)

Example .pkl sitemap (of a _very_ large site):

![image](https://github.com/user-attachments/assets/7e483c40-b57b-419a-96ac-c6110e0cb2c7)





