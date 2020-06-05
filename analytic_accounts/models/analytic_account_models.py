# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
import logging

def cojo_padding_4_right(number):
    return str(number).rjust(4, '0') if type(number) == str else "0000"

def cojo_padding_3_right(number):
    return str(number).rjust(3, '0') if type(number) == str else "000"

def cojo_padding_2_right(number):
    return str(number).rjust(2, '0') if type(number) == str else "00"

_logger_ = logging.getLogger(__name__)

# We add these fields because we can use odoo's Company, Country and State models
class Company(models.Model):
    _inherit = "res.company"
    
    analytic_code = fields.Char(string="Analytic Code")
    
    _sql_constraints = [(
        'analytic_code_unique', 'unique(analytic_code)', 'Analytic Code must be unique!'
    )]

class AnalyticAccounts(models.Model):
    _inherit = "account.analytic.account"

    country_id = fields.Many2one(string="Country", related="company_id.country_id")
    state_id = fields.Many2one(string="State", related="company_id.state_id")
    
    department = fields.Many2one("analytic_accounts.group.department", string="Department")
    sub_department = fields.Many2one("analytic_accounts.group.sub_department", string="Sub Department")
    type = fields.Many2one("analytic_accounts.group.type", string="Type")
    group = fields.Many2one("analytic_accounts.group", string="Group")
    account = fields.Many2one("analytic_accounts.group.account", string="Account")
    sub_account = fields.Many2one("analytic_accounts.group.sub_account", string="Sub Account")
    item = fields.Many2one("analytic_accounts.group.item", string="Item")

    country_rel_id = fields.Integer(string='Country Id', related='country_id.id', readonly=False)
    state_rel_id = fields.Integer(string='State Id', related='state_id.id', readonly=False)
    company_rel_id = fields.Integer(string='Company Id', related='company_id.id', readonly=False)
    department_rel_id = fields.Integer(string='Department Id', related='department.id', readonly=False)
    sub_department_rel_id = fields.Integer(string='Sub Department Id', related='sub_department.id', readonly=False)
    type_rel_id = fields.Integer(string='Type Id', related='type.id', readonly=False)
    group_rel_id = fields.Integer(string='Group Id', related='group.id', readonly=False)
    account_rel_id = fields.Integer(string='Account Id', related='account.id', readonly=False)
    sub_account_rel_id = fields.Integer(string='Sub Account Id', related='sub_account.id', readonly=False)
    item_rel_id = fields.Integer(string='Item Id', related='item.id', readonly=False)
    
    country_rel_code = fields.Char(string='Country Code', related='country_id.code', readonly=False)
    state_rel_code = fields.Char(string='State Code', related='state_id.code', readonly=False)
    company_rel_code = fields.Char(string='Company Code', related='company_id.analytic_code', readonly=False)
    department_rel_code = fields.Char(string='Department Code', related='department.code', readonly=False)
    sub_department_rel_code = fields.Char(string='Sub Department Code', related='sub_department.code', readonly=False)
    type_rel_code = fields.Char(string='Type Code', related='type.code', readonly=False)
    group_rel_code = fields.Char(string='Group Code', related='group.code', readonly=False)
    account_rel_code = fields.Char(string='Account Code', related='account.code', readonly=False)
    sub_account_rel_code = fields.Char(string='Sub Account Code', related='sub_account.code', readonly=False)
    item_rel_code = fields.Char(string='Item Code', related='item.code', readonly=False)
    
    department_rel_name = fields.Char(string='Department Name', related='department.name', readonly=False)
    sub_department_rel_name = fields.Char(string='Sub Department Name', related='sub_department.name', readonly=False)

    def test_foo(self):
        return "test"

    # Domains
    @api.onchange("department")
    def _onchange_department(self):
        if not self.department:
            self.sub_department = False

    @api.onchange("type")
    def _onchange_type(self):
        res = {}
        if self.type:
            res['domain'] = {'group': [('type_id', '=', self.type.id)]}
            self.group = self.type.group_none
        return res
    
    @api.onchange("group")
    def _onchange_group(self):
        res = {}
        if self.group:
            res['domain'] = {'account': [('group_id', '=', self.group.id)]}
            self.account = self.group.account_none
        return res

    @api.onchange("account")
    def _onchange_account(self):
        res = {}
        if self.account:
            res['domain'] = {'sub_account': [('account_id', '=', self.account.id)]}
            self.sub_account = self.account.sub_account_none
        return res

    @api.onchange("sub_account")
    def _onchange_sub_account(self):
        res = {}
        if self.sub_account:
            res['domain'] = {'item': [('sub_account_id', '=', self.sub_account.id)]}
            self.item = self.sub_account.item_none
        return res

    def make_or_change(self, values):
        company_code = cojo_padding_4_right(self.company_id.analytic_code)
        if "company_id" in values:
            if values["company_id"]:
                company = self.env['res.company'].browse(values["company_id"])
                company_code = cojo_padding_4_right(company.analytic_code)
        if not company_code:
            company_code = "0000"
            
        country_code = cojo_padding_2_right(self.country_id.code)
        if "country_id" in values:
            if values["country_id"]:
                country = self.env['res.country'].browse(values["country_id"])
                country_code = country.code
        if not country_code:
            country_code = "00"

        state_code = cojo_padding_3_right(self.state_id.code)
        if "state_id" in values:
            if values["state_id"]:
                state = self.env['res.country.state'].browse(values["state_id"])
                state_code = state.code
        if not state_code:
            state_code = "000"

        department_code = cojo_padding_4_right(self.department.code)
        if "department" in values:
            if values["department"]:
                department = self.env['analytic_accounts.group.department'].browse(values["department"])
                department_code = cojo_padding_4_right(department.code)
            else:
                values["sub_department"] = False
        if not department_code:
            department_code = "0000"

        sub_department_code = cojo_padding_4_right(self.sub_department.code)
        if "sub_department" in values:
            if values["sub_department"]:
                sub_department = self.env['analytic_accounts.group.sub_department'].browse(values["sub_department"])
                sub_department_code = cojo_padding_4_right(sub_department.code)
        if not sub_department_code:
            sub_department_code = "0000"

        type_code = cojo_padding_4_right(self.type.code)
        if "type" in values:
            if values["type"]:
                type_record = self.env['analytic_accounts.group.type'].browse(values["type"])
                type_code = cojo_padding_4_right(type_record.code)
        if not type_code:
            type_code = "0000"

        group_code = cojo_padding_4_right(self.group.code)
        if "group" in values:
            if values["group"]:
                group = self.env['analytic_accounts.group'].browse(values["group"])
                group_code = cojo_padding_4_right(group.code)
        if not group_code:
            group_code = "0000"

        account_code = cojo_padding_4_right(self.account.code)
        if "account" in values:
            if values["account"]:
                account = self.env['analytic_accounts.group.account'].browse(values["account"])
                account_code = cojo_padding_4_right(account.code)
        if not account_code:
            account_code = "0000"

        sub_account_code = cojo_padding_4_right(self.sub_account.code)
        if "sub_account" in values:
            if values["sub_account"]:
                sub_account = self.env['analytic_accounts.group.sub_account'].browse(values["sub_account"])
                sub_account_code = cojo_padding_4_right(sub_account.code)
        if not sub_account_code:
            sub_account_code = "0000"

        item_code = cojo_padding_4_right(self.item.code)
        
        if "item" in values:
            if values["item"]:
                item = self.env['analytic_accounts.group.item'].browse(values["item"])
                item_code = cojo_padding_4_right(item.code)
        if not item_code:
            item_code = "0000"

        code = "{}{}{}{}{}{}{}{}{}{}".format(country_code,
                                             state_code,
                                             company_code,
                                             department_code,
                                             sub_department_code,
                                             type_code,
                                             group_code,
                                             account_code,
                                             sub_account_code,
                                             item_code)

        values["code"] = code

    def _import(self, values):
        code = values["code"]
        _logger_.info("Importing analytic account with reference: {}".format(code))

        if len(code) == 37:
            country_code        = code[0:2]
            region_code         = code[2:5]
            company_code        = code[5:9]
            
            #===================================================================
            # Verifica si la compañia existen en Odoo
            # Tambien comprueba si el country y el region son
            # igualmente validos
            #===================================================================
            
            CompanyEnv = self.env["res.company"]
            company_id = CompanyEnv.search([("analytic_code", "=", company_code)])
            if not company_id:
                raise exceptions.ValidationError(_("Invalid company code, must be 1234"))
            company_record = CompanyEnv.browse([company_id])
            
            if company_record.ids[0].country_id:
                if company_record.ids[0].country_id.code != country_code:
                    raise exceptions.ValidationError(_("Invalid country code, must be 12"))
                if company_record.ids[0].state_id:
                    if company_record.ids[0].state_id.code != region_code:
                        raise exceptions.ValidationError(_("Invalid region/state code, must be 123"))
                else:
                    raise exceptions.ValidationError(_("Country needs state specified"))
            else:
                raise exceptions.ValidationError(_("Company needs country specified"))
                
            department_code     = code[9:13]
            sub_department_code = code[13:17]
            
            type_code           = code[17:21]
            group_code          = code[21:25]
            account_code        = code[25:29]
            sub_account_code    = code[29:33]
            item_code           = code[33:37]
            
            #===================================================================
            # Estos son distinto porque sin independientes y ademas opcionales
            #===================================================================
            DeptEnv = self.env["analytic_accounts.group.department"]
            existing_dept = DeptEnv.search([["code", "=", department_code]])
            if len(existing_dept.ids) > 1:
                _logger_.error("Multiple departments!: {}".format( [r.name for r in existing_dept] ))

            if existing_dept:
                values["department"] = existing_dept.id
            else:
                new_dept= DeptEnv.create({
                        "name": "department-{}".format(department_code),
                        "code": department_code
                    })
                values["department"] = new_dept.id
            
            #===================================================================
            # Type
            #===================================================================
            SubDeptEnv = self.env["analytic_accounts.group.sub_department"]
            existing_sub_department = SubDeptEnv.search([["code", "=", sub_department_code]])
            if len(existing_sub_department.ids) > 1:
                _logger_.error("Multiple sub departments!: {}".format( [r.name for r in existing_sub_department] ))

            if existing_sub_department:
                values["sub_department"] = existing_sub_department.id
            else:
                new_sub_department = SubDeptEnv.create({
                        "name": "sub_department-{}".format(sub_department_code),
                        "code": sub_department_code
                    })
                values["sub_department"] = new_sub_department.id
            
            #===================================================================
            # Todo esto se hace para hacer un "merge" a los
            # datos type, group, account, sub account y item
            #===================================================================
            
            
           
            
            #===================================================================
            # Type
            #===================================================================
            TypeEnv = self.env["analytic_accounts.group.type"]
            existing_type = TypeEnv.search([["code", "=", type_code]])
            if len(existing_type.ids) > 1:
                _logger_.error("Multiple type!: {}".format( [r.name for r in existing_type] ))

            if existing_type:
                values["type"] = existing_type.id
            else:
                new_type = TypeEnv.create({
                        "name": "type-{}".format(type_code),
                        "code": type_code
                    })
                values["type"] = new_type.id
                
            
            #===================================================================
            # Group
            #===================================================================
            GroupEnv = self.env["analytic_accounts.group"]
            existing_group= GroupEnv.search(["&", ("code", "=", group_code), ("type_id", "=", values["type"])])
            if len(existing_group.ids) > 1:
                _logger_.error("Multiple groups!: {}".format( [r.name for r in existing_group] ))

            if existing_group:
                values["group"] = existing_group.id
            else:
                new_group = GroupEnv.create({
                        "name": "group-{}".format(group_code),
                        "type_id": values["type"],
                        "code": group_code
                    })
                values["group"] = new_group.id
            
            #===================================================================
            # Account
            #===================================================================
            AccountEnv = self.env["analytic_accounts.group.account"]
            existing_account= AccountEnv.search(["&", ("code", "=", account_code), ("group_id", "=", values["group"])])
            if len(existing_account.ids) > 1:
                _logger_.error("Multiple account!: {}".format( [r.name for r in existing_account] ))

            if existing_account:
                values["account"] = existing_account.id
            else:
                new_account = AccountEnv.create({
                        "name": "account-{}".format(account_code),
                        "group_id": values["group"],
                        "code": account_code
                    })
                values["account"] = new_account.id
                
            
            #===================================================================
            # Sub Account
            #===================================================================
            SubAccountEnv = self.env["analytic_accounts.group.sub_account"]
            existing_sub_account= SubAccountEnv.search(["&", ("code", "=", sub_account_code), ("account_id", "=", values["account"])])
            if len(existing_sub_account.ids) > 1:
                _logger_.error("Multiple sub account!: {} in account: {}".format( [r.name for r in existing_sub_account], values["account"]))

            if existing_sub_account:
                values["sub_account"] = existing_sub_account.id
            else:
                new_sub_account = SubAccountEnv.create({
                        "name": "sub_account-{}".format(sub_account_code),
                        "account_id": values["account"],
                        "code": sub_account_code
                    })
                values["sub_account"] = new_sub_account.id
                
            
            #===================================================================
            # Item
            #===================================================================
            ItemEnv = self.env["analytic_accounts.group.item"]
            existing_item = ItemEnv.search(["&", ("code", "=", item_code), ("sub_account_id", "=", values["sub_account"])])
            if len(existing_item.ids) > 1:
                _logger_.error("Multiple items!: {}".format( [r.name for r in existing_item] ))

            if existing_item:
                values["item"] = existing_item.id
            else:
                new_item = ItemEnv.create({
                        "name": "account-{}".format(item_code),
                        "sub_account_id": values["sub_account"],
                        "code": item_code
                    })
                values["item"] = new_item.id
        else:
            raise exceptions.ValidationError(_("Cosas de la vida ¯\_()_/¯"))
        pass


    def change_groups(self, values):
        
        department = values["department"] if "department" in values else self.department_rel_id
        AnalyticGroupEnv = self.env["account.analytic.group"]

        department_group_id = False
        if department:
            
            Deparments = self.env["analytic_accounts.group.department"]
            department = Deparments.browse(department)
            
            ExistingDeptGroup = AnalyticGroupEnv.search(("&", ["parent_id", "=", False],["analytic_code", "=", department.code]))
            
            if not ExistingDeptGroup:
                print("DeptGroupBefore: {}".format(ExistingDeptGroup))
                
                print("Departament: {}".format(department.name))
                
                
                dept_dict_obj = {
                    "name": department.name,
                    "analytic_code": department.code,
                    "description": "Code: {}".format(department.code)
                }
                
                department_group_id = AnalyticGroupEnv.create(dept_dict_obj).id
            else:
                ExistingDeptGroup.write({
                    "name": department.name,
                    "analytic_code": department.code
                })
                department_group_id = ExistingDeptGroup.id
            
        # department_group_id = department_group_id if department_group_id else department.id     
        values["group_id"] = department_group_id 
        SubDeparments = self.env["analytic_accounts.group.sub_department"]

        sub_department = values["sub_department"] if "sub_department" in values else self.sub_department_rel_id

        if sub_department:
            sub_department = SubDeparments.browse(sub_department)
            ExistingSubDeptGroup = AnalyticGroupEnv.search(("&", ["parent_id.analytic_code", "=", department.code], ["analytic_code", "=", sub_department.code ]))
            
            if not ExistingSubDeptGroup:
            
                print("Sub departament: {}".format(sub_department.name))
                sub_dept_dict_obj = {
                    "name": sub_department.name,
                    "parent_id": department_group_id,
                    "analytic_code": sub_department.code,
                    "description": "Code: {}".format(sub_department.code)
                }
                
                sub_dept = AnalyticGroupEnv.create(sub_dept_dict_obj)
                values["group_id"] = sub_dept.id
            else:
                ExistingSubDeptGroup.write({
                    "name": sub_department.name,
                    "analytic_code": sub_department.code
                })
                values["group_id"] = ExistingSubDeptGroup.id

    def reload_dept_code(self, values):
        if "department_rel_code" in values:
            department = None
            if "department" in values:
                department = self.env["analytic_accounts.group.department"].browse([values["department"]])
            elif self.department:
                department = self.department
            else:
                return
            department.code = values["department_rel_code"]

    def reload_sub_dept_code(self, values):
        if "sub_department_rel_code" in values:
            sub_department = None
            if "sub_department" in values:
                sub_department = self.env["analytic_accounts.group.sub_department"].browse([values["sub_department"]])
            elif self.sub_department:
                sub_department = self.sub_department
            else:
                return
            sub_department.code = values["sub_department_rel_code"]


    def reload_type_code(self, values):
        if "type_rel_code" in values:
            type_record = None
            if "type" in values:
                type_record = self.env["analytic_accounts.group.type"].browse([values["type"]])
            elif self.type:
                type_record = self.type
            else:
                return
            type_record.code = values["type_rel_code"]

    def reload_group_code(self, values):
        if "group_rel_code" in values:
            group_record = None
            if "group" in values:
                group_record = self.env["analytic_accounts.group.group"].browse([values["group"]])
            elif self.group:
                group_record = self.group
            else:
                return
            group_record.code = values["group_rel_code"]

    def reload_account_code(self, values):
        if "account_rel_code" in values:
            account_record = None
            if "account" in values:
                account_record = self.env["analytic_accounts.group.account"].browse([values["account"]])
            elif self.account:
                account_record = self.account
            else:
                return
            account_record.code = values["account_rel_code"]

    def reload_sub_account_code(self, values):
        if "sub_account_rel_code" in values:
            sub_account_record = None
            if "sub_account" in values:
                sub_account_record = self.env["analytic_accounts.group.sub_account"].browse([values["sub_account"]])
            elif self.sub_account:
                sub_account_record = self.sub_account
            else:
                return
            sub_account_record.code = values["sub_account_rel_code"]

    def reload_item_code(self, values):
        if "item_rel_code" in values:
            item_record = None
            if "item" in values:
                item_record = self.env["analytic_accounts.group.item"].browse([values["item"]])
            elif self.item:
                item_record = self.item
            else:
                return
            item_record.code = values["item_rel_code"]

    @api.model
    def create(self, values):
        # self.ensure_one()
        self.reload_dept_code(values)
        self.reload_sub_dept_code(values)

        self.reload_type_code(values)
        self.reload_type_code(values)
        self.reload_account_code(values)
        self.reload_sub_account_code(values)
        self.reload_item_code(values)

        if "group_id" in values:
            self.make_or_change(values)
        else:
            self._import(values)

        # Create a group based on department and sub department
        self.change_groups(values)
            
        return super(AnalyticAccounts, self).create(values)

    def write(self, values):
        self.ensure_one()
        
        self.reload_dept_code(values)
        self.reload_sub_dept_code(values)

        self.reload_type_code(values)
        self.reload_type_code(values)
        self.reload_account_code(values)
        self.reload_sub_account_code(values)
        self.reload_item_code(values)
        
        self.make_or_change(values)
        self.change_groups(values)
        
        return super().write(values)

# Just simply to make these groups
class GroupBase(models.Model):
    _name = "analytic_accounts.group.base"

    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code", required=True, size=4)
    
    @api.model
    def create(self, values):
        
        if "code" in values:
            values["code"] = values["code"].rjust(4, "0")[-4:]
                    
        return super(GroupBase, self).create(values)
    
    
    def write(self, values):
        # print("Creando un grupo generico")
        if "code" in values:
            values["code"] = cojo_padding_4_right(values["code"])
                    
        return super(GroupBase, self).write(values)


class GroupDepartment(GroupBase):
    _name = "analytic_accounts.group.department"

    # group_id = fields.Many2one("account.analytic.group", string="Group")

    # def write(self, values):
    #     if "name" in values:
    #         group_id.write({
    #             "name": values["name"]
    #         })
    #     return super().write(values)

class GroupSubDepartment(GroupBase):
    _name = "analytic_accounts.group.sub_department"

    #group_id = fields.Many2one("account.analytic.group", string="Group")

    #def write(self, values):
    #    if "name" in values:
    #        group_id.write({
    #            "name": values["name"]
    #        })
    #    return super().write(values)

class GroupType(GroupBase):
    _name = "analytic_accounts.group.type"
    
    # sub_department.id = fields.Many2one("analytic_accounts.group.sub_department", required=True)
    group_ids = fields.One2many("analytic_accounts.group", "type_id", ondelete="cascade")
    group_none = fields.Many2one("analytic_accounts.group")
    
    @api.model
    def create(self, values):
        res = super().create(values)
        
        none_group = self.env["analytic_accounts.group"].create({
            "type_id": res.id,
            "code": "0000",
            "name": "None"
        })
        
        res.group_none = none_group.id
        
        return res


class Group(GroupBase):
    _name = "analytic_accounts.group"

    type_id = fields.Many2one("analytic_accounts.group.type", required=True, ondelete="cascade")
    account_ids = fields.One2many("analytic_accounts.group.account", "group_id", ondelete="cascade")
    account_none = fields.Many2one("analytic_accounts.group.account")
    
    @api.model
    def create(self, values):
        if not "type_id" in values:
            values["type_id"] = self._context.get("type_id")
        res = super().create(values)
        
        #=======================================================================
        # print(res)
        #=======================================================================
        
        none_account = self.env["analytic_accounts.group.account"].create({
            "group_id": res.id,
            "code": "0000",
            "name": "None"
        })
        
        res.account_none = none_account.id
        
        return res


class GroupAccount(GroupBase):
    _name = "analytic_accounts.group.account"

    group_id = fields.Many2one("analytic_accounts.group", required=True, ondelete="cascade")
    sub_account_ids = fields.One2many("analytic_accounts.group.sub_account", "account_id", ondelete="cascade")
    sub_account_none = fields.Many2one("analytic_accounts.group.sub_account")
    
    @api.model
    def create(self, values):
        if not "group_id" in values:
            values["group_id"] = self._context.get("group_id")
        res = super().create(values)
        
        none_sub_account = self.env["analytic_accounts.group.sub_account"].create({
            "account_id": res.id,
            "code": "0000",
            "name": "None"
        })
        
        res.sub_account_none = none_sub_account.id
        
        return res


class GroupSubAccount(GroupBase):
    _name = "analytic_accounts.group.sub_account"

    account_id = fields.Many2one("analytic_accounts.group.account", required=True, ondelete="cascade")
    item_ids = fields.One2many("analytic_accounts.group.item", "sub_account_id", ondelete="cascade")
    item_none = fields.Many2one("analytic_accounts.group.item")
    
    @api.model
    def create(self, values):
        if not "account_id" in values:
            values["account_id"] = self._context.get("account_id")
        res = super().create(values)
        
        none_item = self.env["analytic_accounts.group.item"].create({
            "sub_account_id": res.id,
            "code": "0000",
            "name": "None"
        })
        
        res.item_none = none_item.id
        
        return res


class GroupItem(GroupBase):
    _name = "analytic_accounts.group.item"

    sub_account_id = fields.Many2one("analytic_accounts.group.sub_account", ondelete="cascade") 
    
    @api.model
    def create(self, values):
        if not "sub_account_id" in values:
            values["sub_account_id"] = self._context.get("sub_account_id")
        res = super().create(values)
        return res
