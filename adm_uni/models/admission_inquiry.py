# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
from ..utils import formatting


class Status(models.Model):
    _name = "adm_uni.inquiry.status"
    _order = "sequence"

    

    name = fields.Char(string="Status Name")
    description = fields.Text(string="Description")
    sequence = fields.Integer(readonly=True, default=-1)
    fold = fields.Boolean(string="Fold")
    type = fields.Selection((('stage', "Stage"),
                             ('done', "Done"),
                             ('cancelled', 'Cancelled')),
                            string="Type", default='stage')
    task_ids = fields.One2many("adm_uni.inquiry.task", "status_id", "Status Ids")

    @api.model
    def create(self, values):
        next_order = self.env['ir.sequence'].next_by_code('sequence.inquiry.task')

        values['sequence'] = next_order
        return super(Status, self).create(values)


class Inquiry(models.Model):
    _name = "adm_uni.inquiry"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _primary_email = ['email']

    @api.model
    def _read_group_status_ids(self,stages,domain,order):
        status_ids = self.env['adm_uni.inquiry.status'].search([])
        return status_ids
    
    # Admission Information
    preferred_degree_program = fields.Many2one("adm_uni.degree_program",
                                               string="Preferred Degree Program")
    
    # Demographic
    name = fields.Char(string="Name", default="Undefined", readonly=True)
    first_name = fields.Char(string="First Name", default="")
    middle_name = fields.Char(string="Middle Name", default="")
    last_name = fields.Char(string="Last Name", default="")
    birthdate = fields.Date(string="Birthdate")
    gender = fields.Selection((('m', 'Male'), ('f', 'Female')), string="Gender")

    # Contact
    email = fields.Char(string="Email", related="partner_id.email", index=True)
    phone = fields.Char(string="Phone", related="partner_id.phone")
    
    # School
    current_school = fields.Char(string="Current School")
    current_school_address = fields.Char(string="Current School Address")
    
    # Skills
    language_ids = fields.One2many("adm_uni.inquiry.languages", "inquiry_id",
                                    string="Languages")
    
    # Location
    country_id = fields.Many2one("res.country", related="partner_id.country_id", string="Country")
    state_id = fields.Many2one("res.country.state", related="partner_id.state_id", string="State")
    city = fields.Char(string="City", related="partner_id.city")
    street_address = fields.Char(string="Street Address", related="partner_id.street")
    zip = fields.Char("zip", related="partner_id.zip")
    
    
    partner_id= fields.Many2one("res.partner", string="Contact")
    status_id = fields.Many2one("adm_uni.inquiry.status",
                                string="Status", group_expand="_read_group_status_ids")
    task_ids = fields.Many2many("adm_uni.inquiry.task")

    state_tasks = fields.One2many(string="State task", related="status_id.task_ids")

    status_type = fields.Selection(string="Status Type", related="status_id.type")

    application_id = fields.Many2one("adm_uni.application")
    forcing = False
    
    
    def message_get_suggested_recipients(self):
        recipients = super().message_get_suggested_recipients() 
        try:
            for inquiry in self:
                if inquiry.email:
                    inquiry._message_add_suggested_recipient(recipients, partner=self.partner_id, email=inquiry.email, reason=_('Custom Email Luis'))
        except exceptions.AccessError:  # no read access rights -> just ignore suggested recipients because this imply modifying followers
            pass
        return recipients

    def force_back(self):
        status_ids_ordered = self.env['adm_uni.inquiry.status'].search([], order="sequence")
        index = 0
        for status in status_ids_ordered:
            if status == self.status_id:
                break
            index += 1

        index -= 1
        if index >= 0:
            next_status = status_ids_ordered[index]
            self.forcing = True
            self.status_id = next_status

    def force_next(self):
        status_ids_ordered = self.env['adm_uni.inquiry.status'].search([], order="sequence")
        index = 0
        for status in status_ids_ordered:
            if status == self.status_id:
                break
            index += 1

        index += 1
        if index < len(status_ids_ordered):
            next_status = status_ids_ordered[index]
            self.forcing = True
            self.status_id = next_status

    def move_to_next_status(self):
        status_ids_ordered = self.env['adm_uni.inquiry.status'].search([], order="sequence")
        index = 0
        for status in status_ids_ordered:
            if status == self.status_id:
                break
            index += 1

        index += 1
        if index < len(status_ids_ordered):
            next_status = status_ids_ordered[index]

            if self.status_id.type == 'done':
                raise exceptions.except_orm(_('Inquiry completed'), _('The Inquiry is already done'))
            elif self.status_id.type == 'cancelled':
                raise exceptions.except_orm(_('Inquiry cancelled'), _('The Inquiry cancelled'))
            else:
                self.status_id = next_status

    def cancel(self):
        status_ids_ordered = self.env['adm_uni.inquiry.status'].search([], order="sequence")
        for status in status_ids_ordered:
            if status.type == 'cancelled':
                self.status_id = status
                break

    @api.onchange("first_name", "middle_name", "last_name")
    def _set_full_name(self):
        self.name = formatting.format_name(self.first_name, self.middle_name, self.last_name) 

    @api.onchange("country_id")
    def _onchange_country_id(self):
        res = {}
        if self.country_id:
            res['domain'] = {'state_id': [('country_id', '=', self.country_id.id)]}

    @api.model
    def create(self, values):
        first_status = self.env['adm_uni.inquiry.status'].search([], order="sequence")[0]
        values['status_id'] = first_status.id
        values['name'] = formatting.format_name(values['first_name'], values['middle_name'], values['last_name']) 
        
        inquiry = super().create(values)
        
        partner = self.create_new_partner(values)
        partner.uni_inquiry_id = inquiry.id
        
        inquiry.partner_id = partner.id
        
        return inquiry

    def create_new_partner(self, values):
        PartnerEnv = self.env["res.partner"]
          
        partner = PartnerEnv.create({
            "name": values["name"], 
            "email": values["email"],
            "phone": values["phone"],
            "country_id": values["country_id"],
            "state_id": values["state_id"],
            "city": values["city"],
            "street": values["street_address"],
            "zip": values["zip"],
        })
         
        
        #===============================================================================================================
        # user = UsersEnv.create({
        #     "name": values["name"],
        #     "partner_id": partner.id,
        #     "login": values["email"],
        #     "sel_groups_1_9_10": 9,
        # })
        #===============================================================================================================
         
        return partner
    
    
    def create_new_application(self):
        print("Create New Application")
        
        #===============================================================================================================
        # # Create Contact
        # Partner = User
        # user = super(ResUsers, self).create(values)
        # if user.email and not self.env.context.get('no_reset_password'):
        #     try:
        #         user.with_context(create_user=True).action_reset_password()
        #     except MailDeliveryException:
        #         user.partner_id.with_context(create_user=True).signup_cancel()
        # return user
        #===============================================================================================================
        
        ApplicationEnv = self.env["adm_uni.application"]
        
        application_record = ApplicationEnv.create({
            "name": self.name,
            "first_name": self.first_name,
            "middle_name": self.middle_name,
            "last_name": self.last_name,
            "birthdate": self.birthdate,
            "gender": self.gender,
            
            "current_school": self.current_school,
            "current_school_address": self.current_school_address,
            
            "partner_id": self.partner_id.id,
        })
        
        # Creating languages
        for language in self.language_ids:
            
            ApplicationLanguageEnv = self.env["adm_uni.application.languages"]
            
            ApplicationLanguageEnv.create({
                "language_id": language.language_id.id,
                "language_level_id": language.language_level_id.id,
                "application_id": application_record.id,
            })
             
        self.partner_id.uni_application_id = application_record.id
        self.application_id = application_record.id
        application_record.inquiry_id = self.id
        
        UsersEnv = self.env["res.users"]
        user = UsersEnv.create({
            "name": self.name,
            "partner_id": self.partner_id.id,
            "login": self.email,
            "sel_groups_1_9_10": 9,
        })

    
    def write(self, values):

        # print(self.task_ids)
        # print(self.state_tasks)
        #
        # self.condition = ()
        # print(self.condition)

        StatusEnv = self.env['adm_uni.inquiry.status'] 
        status_ids = StatusEnv.search([])

        print(status_ids)


        if "status_id" in values and not self.forcing:
            if not self.state_tasks & self.task_ids == self.state_tasks and self:
                raise exceptions.ValidationError("All task are not completed")
        else:
            self.forcing = False

        inquiry = super().write(values)
        self.partner_id.name = self.name
        
        if "status_id" in values:
            next_status = StatusEnv.browse([values["status_id"]])
            if (next_status.type == "done" and 
                not self.application_id):
                self.create_new_application()
        
        return inquiry

    
    def unlink(self):
        print("Borrado")
        return super(Inquiry, self).unlink()

    # Mail integration
    # message_follower_ids
    
    def message_get_default_recipients(self):
        return {
            r.id : {'partner_ids': [],
                    'email_to': r.email}
            for r in self.sudo()
        }
        
    @api.model
    def message_new(self, msg_dict, custom_values=None):
        """ Overrides mail_thread message_new that is called by the mailgateway
            through message_process.
            This override updates the document according to the email.
        """
        # remove default author when going through the mail gateway. Indeed we
        # do not want to explicitly set user_id to False; however we do not
        # want the gateway user to be responsible if no other responsible is
        # found.
        self = self.with_context(default_user_id=False)

        if custom_values is None:
            custom_values = {}
        defaults = {
            'name':  msg_dict.get('subject') or _("No Subject"),
            'email_from': msg_dict.get('from'),
            'email_cc': msg_dict.get('cc'),
            'partner_id': msg_dict.get('author_id', False),
        }
        if msg_dict.get('author_id'):
            defaults.update(self._onchange_partner_id_values(msg_dict.get('author_id')))
        if msg_dict.get('priority') in dict(crm_stage.AVAILABLE_PRIORITIES):
            defaults['priority'] = msg_dict.get('priority')
        defaults.update(custom_values)

        # assign right company
        if 'company_id' not in defaults and 'team_id' in defaults:
            defaults['company_id'] = self.env['crm.team'].browse(defaults['team_id']).company_id.id
        return super().message_new(msg_dict, custom_values=defaults)

        
class InquiryTasks(models.Model):
    _name = "adm_uni.inquiry.task"

    name = fields.Char("Name")
    description = fields.Char("Description")
    status_id = fields.Many2one("adm_uni.inquiry.status", string="Status")

    
class AdmissionInquiryLanguages(models.Model):
    _name = "adm_uni.inquiry.languages"
    
    language_id = fields.Many2one("adm_uni.languages", string="Language")
    language_level_id = fields.Many2one("adm_uni.languages.level", string="Language Level")
    inquiry_id = fields.Many2one("adm_uni.inquiry", string="Inquiry")
    