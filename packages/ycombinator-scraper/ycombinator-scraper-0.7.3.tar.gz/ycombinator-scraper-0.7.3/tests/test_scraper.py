from ycombinator_scraper.models import CompanyData, FounderData, JobData


def test_successful_login(scraper, get_test_url):
    username = "test_user"
    password = "test_password"
    result = scraper.login(username, password)
    assert result is True
    scraper.shutdown_driver()


def test_scrape_job_data(scraper, get_test_url):
    job_url = get_test_url

    job_data = scraper.scrape_job_data(job_url)

    assert isinstance(job_data, JobData)

    assert job_data.job_url == job_url
    assert isinstance(job_data.job_title, str)
    assert isinstance(job_data.job_tags, list)
    assert isinstance(job_data.job_salary_range, str)
    assert isinstance(job_data.job_description, str)
    scraper.shutdown_driver()


def test_scrape_company_data(scraper, get_test_url):
    company_url = get_test_url

    company_data = scraper.scrape_company_data(company_url)

    assert isinstance(company_data, CompanyData)
    assert company_data.company_url == company_url
    assert isinstance(company_data.company_image, str)
    assert isinstance(company_data.company_name, str)
    assert isinstance(company_data.company_description, str)
    assert isinstance(company_data.company_tags, list)
    assert isinstance(company_data.company_job_links, list)
    assert isinstance(company_data.company_social_links, list)

    scraper.shutdown_driver()


def test_scrape_founders_data(scraper, get_test_url):
    company_url = get_test_url

    founders_list = scraper.scrape_founders_data(company_url)

    assert all(isinstance(founder, FounderData) for founder in founders_list)

    for founder in founders_list:
        assert isinstance(founder.founder_name, str)
        assert isinstance(founder.founder_image_url, str)
        assert isinstance(founder.founder_description, str)
        assert isinstance(founder.founder_linkedin_url, str)

    scraper.shutdown_driver()
