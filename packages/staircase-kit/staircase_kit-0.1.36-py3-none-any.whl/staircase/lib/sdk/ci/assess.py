import time


def assess(self, source_url):
    r = self.CI_ENV.assess_product.assess(source_url)
    id_ = r["assessment_id"]
    while True:
        response_body = self.CI_ENV.assess_product.check_assessment(id_)
        status = response_body.get("status")
        print(f"Status of assess: {status}")
        if status in ("IN_PROGRESS", "RUNNING"):
            time.sleep(15)
        elif status == "FAILED":
            print(f"Assess failed")
            if logs := response_body.get("logs"):
                logs = "".join(logs) if isinstance(logs, list) else logs
            print(response_body)
            return source_url
        else:
            source_url = response_body["source_url"]
            return source_url
