import cfao as cf


def scrape_cfao():
    """Scrape fire enforcement notices."""

    ### Input ###

    # Search name
    search_name = "all"

    # Search parameters
    search = dict()
    search['premises_type_id'] = ''
    search['premises_id'] = ''
    search['fire_service_id'] = ''
    search['organisation_name'] = ''
    search['responsible_person'] = ''
    search['address'] = ''
    search['postcode'] = ''
    search['status_id'] = ''

    # Results per scrapped page
    res_per_page = 50

    # Csv output filename
    csv_file = 'notices.csv'

    ### Processing ###

    search_params = cf.create_search_params(search)

    count_url = cf.create_cfoa_url(1, 1, search_params)

    search_hits = cf.extract_search_count(count_url)

    search_details = cf.create_search_metadata(
            search_name,
            search,
            search_hits
    )

    num_scrape_pages = cf.calculate_num_scrape_pages(search_hits, res_per_page)

    header = cf.scrape_result_pages(num_scrape_pages, res_per_page, search_params)

    notices = cf.scrape_detail_pages(header, search_details)

    ### Output ###

    # Save as csv file
    cf.create_notice_csv(notices, csv_file)


if __name__ == "__main__":
    scrape_cfao()

