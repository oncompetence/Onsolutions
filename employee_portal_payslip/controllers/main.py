from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal
from datetime import date


class PortalPayslips(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        employee = request.env.user.employee_ids[:1]
        domain = [("employee_id", "=", employee.id), ("state", "=", "done")]
        values["payslip_count"] = request.env["hr.payslip"].search_count(domain)
        return values

    @http.route(["/my/payslips"], type="http", auth="user", website=True)
    def portal_payslips(self, **kwargs):
        employee = request.env.user.employee_ids[:1]
        payslips = (
            request.env["hr.payslip"]
            .sudo()
            .search(
                [
                    ("employee_id", "=", employee.id),
                    ("state", "=", "validated"),
                ]
            )
        )

        return request.render(
            "employee_portal_payslip.portal_payslip_list",
            {
                "payslips": payslips.sudo(),
            },
        )

    @http.route(
        ["/my/payslips/<int:payslip_id>/print"], type="http", auth="user", website=True
    )
    def portal_payslip_print(self, payslip_id):
        payslip = request.env["hr.payslip"].sudo().browse(payslip_id)
        if payslip.employee_id.user_id.id != request.uid:
            return request.redirect("/my")

        pdf, _ = request.env["ir.actions.report"]._render_qweb_pdf(
            "hr_payroll.action_report_payslip", payslip.id
        )
        pdfhttpheaders = [
            ("Content-Type", "application/pdf"),
            ("Content-Length", len(pdf)),
            (
                "Content-Disposition",
                'attachment; filename="recibo_%s.pdf"' % payslip.name,
            ),
        ]
        return request.make_response(pdf, headers=pdfhttpheaders)


    @http.route(["/my/payslips/<int:payslip_id>/sign"], type="http", auth="user", website=True)
    def portal_payslip_sign(self, payslip_id, **kwargs):
        payslip = request.env["hr.payslip"].sudo().browse(payslip_id)
        
        if payslip.employee_id.user_id.id != request.uid:
            return request.redirect("/my")
        
        if request.httprequest.method == "POST":
            signature = kwargs.get("signature")
            if signature:
                payslip.sudo().write({
                    "employee_signature": signature,
                    "signed_date": date.today(),
                })
            return request.redirect("/my/payslips")
        
        return request.render("employee_portal_payslip.portal_payslip_sign", {
            "payslip": payslip,
        })