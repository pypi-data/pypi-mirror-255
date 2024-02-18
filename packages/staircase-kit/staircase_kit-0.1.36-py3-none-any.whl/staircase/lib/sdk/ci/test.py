import time


def test(self, source_url):
    r = self.CI_ENV.test_product.test_ui(source_url)
    id_ = r["test_suites_invoked"][0]["uiTests"]

    while True:
        response_body = self.CI_ENV.test_product.check(id_)
        status = response_body.get("status")
        if status in ("IN_PROGRESS", "RUNNING"):
            time.sleep(15)
        elif status == "FAILED":
            print(response_body)
            return
        else:
            print(response_body)
            return
