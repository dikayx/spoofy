from flask import Blueprint, render_template, request
from spoofable.utils import check_mx_record, check_spf_record, check_dmarc_record, check_dkim_record

blueprint = Blueprint('routes', __name__)

@blueprint.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form.get('url')

        # Perform checks and get records
        mx_valid, mx_records = check_mx_record(url)
        spf_valid, spf_record = check_spf_record(url)
        dmarc_valid, dmarc_record, dmarc_assessment = check_dmarc_record(url)
        dkim_valid, dkim_record = check_dkim_record(url)

        results = {
            "mx_record": {"valid": mx_valid, "records": mx_records},
            "spf_record": {"valid": spf_valid, "records": spf_record},
            "dmarc_record": {
                "valid": dmarc_valid,
                "records": dmarc_record,
                "assessment": dmarc_assessment,
            },
            "dkim_record": {"valid": dkim_valid, "records": dkim_record},
        }

        return render_template('index.html', domain=url, results=results)

    # Landing page
    return render_template('index.html')
