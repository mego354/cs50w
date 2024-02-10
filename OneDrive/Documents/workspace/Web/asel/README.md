Al Asel Store:

Al Asel is a kit shop owned by a friend, specializing in selling equipment and various related items. Currently, transactions are managed using Excel, which may not be the most efficient or accurate method. To address this, I envisioned a specialized system tailored for managing the store's operations, from inventory and orders to client management and sales analysis. This report outlines the key components and functionalities of the proposed system.

Distinctiveness and Complexity:

File Structure:

The application comprises over 25 HTML pages and 2 layout templates. One layout is dedicated to standard or main pages, while the other serves for alternate pages. Additionally, there are static files including a logo and a main CSS file containing all styles. JavaScript files contain functions utilized across different HTML pages to optimize code reuse.

Running the Application:

Creating an Order:
On the home page, the cashier can select products to include in an order. The items are covered in a category box, which can be hidden by clicking on it for a cleaner interface. After specifying quantities and selecting the client (regular or branch has sold the order to random buyer) and type of the order (regular, wholesale), the form is submitted to proceed to the order's page. Here, additional actions such as adding offers, modifying prices or quantities, and removing or adding items are possible.

Inserting an Order:
Alternatively, users can input orders already made by the owner. This involves specifying quantities for each item, identifying the seller of the order, and selecting an accepting branch. Orders are sorted in a sorted way starting from the most recent order to the oldest, allowing for easy tracking and management. Different features are available for modifying orders, including adjusting prices due to changes and ensuring orders are closed once edited to prevent potential bugs.

The application also facilitates creating items, categories, and clients (both suppliers and buyers). It allows for recording partial payments and displaying unpaid amounts, with details accessible by clicking on client names (in the top of the client's page under the percentage bar which is the percent of all the money that the user have to pay in general and how much is the rest of it).

then the view of clients, orders:
orders arranged by the most recent ones, and you can just type the id and click enter to open a specific order,
besides the clients search bar can help you by serching in the name, id of the user and get you the all possible results for your search and the enter leads you to the most suggest in the top.

each client page contains all of his orders, arranged as well as the user can hide months or years to focus on a specific duration.

if the client is also a branch page it their page must have a link in the top leads you to the provided orders and also the percentage and the payments details


Details of Sales Pages:

The sales section of the application offers in-depth analysis and visualization of sales data. It includes the following components:

Sales Overview: Provides a comprehensive overview of sales data across all years, offering insights into overall performance.

Yearly Breakdown: Allows users to delve into sales data for each year individually. Users can analyze sales trends, and revenue generated for each year.

Monthly Analysis: Within each yearly breakdown, users can further explore sales data on a monthly basis. This granular view enables tracking of monthly sales fluctuations and identification of peak periods. Users can also hide each month's orders or the whole year for better focus and analysis besides that the only opened year is the recent one.

Graphical Representation: Utilizes various chart types, such as bar graphs and pie charts, from chartjs and Google Charts. These graphical representations enhance data interpretation and facilitate quick insights into sales trends.

Detailed Reports: Provides detailed reports containing specific sales metrics, including total revenue, average order value, and top-selling products. These reports offer valuable insights for strategic decision-making and business planning.

Project Distinctiveness and Complexity:

The project is distinct and complex due to the following reasons:

Utilization of around 7 models, demonstrating originality and depth in design.
Integration of external resources such as Chart.js, Google Charts, Font Awesome icons, and Google Fonts, enhancing the visual appeal and functionality of the application.
The system addresses real-life business needs, offering a tailored solution for managing a retail store's operations efficiently.
It accommodates various scales of operation and is not limited to mobile devices, ensuring flexibility and usability across different contexts.

i've used:
chartjs, google fonts, google charts and font awesome for the icons all as cdn s no need for installing any other libraries than django's


Conclusion:

In conclusion, the Al Asel Store management system is a comprehensive solution designed to streamline operations and enhance efficiency in managing inventory, orders, clients, and sales analysis. Its distinctive features, complexity, and integration of external resources make it a robust solution for modern retail management needs.