# Wikipedia Scraper

### Scraper looking for the shortest route between two Wikipedia pages

![prev](assets/wikiscraperprev.gif)

The Wikipedia Scraper is a tool designed to find the shortest path between two Wikipedia pages. It automatically navigates links on a starting page, then continues to navigate through the pages that have been scraped, until it finds the target page. It operates on the principle of a graph search algorithm ([BFS](https://en.wikipedia.org/wiki/Breadth-first_search)), seeking the shortest path between two pages.

---

- Program begins by scraping links from the starting page, then checks if the destination page is among them. If not, it continues to scrape links from the subsequent pages until it finds the target page
- Program saves different search results as separate tables in sqlite
- It is possible to resume the unfinished search from the moment it was interrupted, the program will still return the shortest path needed to travel
- Search results can be found in the [db folder](db), as an sql file and written out in the md file