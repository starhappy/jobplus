import os
from flask import url_for
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, ValidationError, IntegerField, TextAreaField, SelectField
from flask_wtf.file import FileField, FileRequired
from wtforms.validators import Length, Email, EqualTo, Required
from jobplus.models import db, User, CompanyDetail, Job


class LoginForm(FlaskForm):
    email = StringField('??', validators=[Required(), Email()])
    password = PasswordField('??', validators=[Required(), Length(6, 24)])
    remember_me = BooleanField('???')
    submit = SubmitField('??')

    def validate_email(self, field):
        if field.data and not User.query.filter_by(email=field.data).first():
            raise ValidationError('??????')

    def validate_password(self, field):
        user = User.query.filter_by(email=self.email.data).first()
        if user and not user.check_password(field.data):
            raise ValidationError('????')


class RegisterForm(FlaskForm):
    name = StringField('???', validators=[Required(), Length(3, 24)])
    email = StringField('??', validators=[Required(), Email()])
    password = PasswordField('??', validators=[Required(), Length(6, 24)])
    repeat_password = PasswordField('????', validators=[Required(), EqualTo('password')])
    submit = SubmitField('??')

    def validate_username(self, field):
        if User.query.filter_by(name=field.data).first():
            raise ValidationError('??????')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('??????')

    def create_user(self):
        user = User(name=self.name.data,
                    email=self.email.data,
                    password=self.password.data)
        db.session.add(user)
        db.session.commit()
        return user


class UserProfileForm(FlaskForm):
    real_name = StringField('??', [Required()])
    email = StringField('??', validators=[Required(), Email()])
    password = PasswordField('??(???????)')
    phone = StringField('???')
    work_years = IntegerField('????')
    resume = FileField('????', validators=[FileRequired()])
    submit = SubmitField('??')

    def validate_phone(self, field):
        phone = field.data
        if phone[:2] not in ('13', '15', '18') and len(phone) != 11:
            raise ValidationError('?????????')

    def upload_resume(self):
        f = self.resume.data
        filename = self.real_name.data + '.pdf'
        f.save(os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            'static',
            'resumes',
            filename
        ))
        return filename

    def update_profile(self, user):
        user.real_name = self.real_name.data
        user.email = self.email.data
        if self.password.data:
            user.password = self.password.data
        user.phone = self.phone.data
        user.work_years = self.work_years.data
        filename = self.upload_resume()
        user.resume_url = url_for('static', filename=os.path.join('resumes', filename))
        db.session.add(user)
        db.session.commit()


class CompanyProfileForm(FlaskForm):
    name = StringField('????')
    email = StringField('??', validators=[Required(), Email()])
    phone = StringField('???')
    password = PasswordField('??(???????)')
    slug = StringField('Slug', validators=[Required(), Length(3, 24)])
    location = StringField('??', validators=[Length(0, 64)])
    site = StringField('????', validators=[Length(0, 64)])
    logo = StringField('Logo')
    description = StringField('?????', validators=[Length(0, 100)])
    about = TextAreaField('????', validators=[Length(0, 1024)])
    submit = SubmitField('??')

    def validate_phone(self, field):
        phone = field.data
        if phone[:2] not in ('13', '15', '18') and len(phone) != 11:
            raise ValidationError('?????????')

    def updated_profile(self, user):
        user.name = self.name.data
        user.email = self.email.data
        if self.password.data:
            user.password = self.password.data

        if user.detail:
            detail = user.detail
        else:
            detail = CompanyDetail()
            detail.user_id = user.id
        self.populate_obj(detail)
        db.session.add(user)
        db.session.add(detail)
        db.session.commit()


class UserEditForm(FlaskForm):
    email = StringField('??', validators=[Required(), Email()])
    password = PasswordField('??')
    real_name = StringField('??')
    phone = StringField('???')
    submit = SubmitField('??')

    def update(self, user):
        self.populate_obj(user)
        if self.password.data:
            user.password = self.password.data
        db.session.add(user)
        db.session.commit()


class CompanyEditForm(FlaskForm):
    name = StringField('????')
    email = StringField('??', validators=[Required(), Email()])
    password = PasswordField('??')
    phone = StringField('???')
    site = StringField('????', validators=[Length(0, 64)])
    description = StringField('?????', validators=[Length(0, 100)])
    submit = SubmitField('??')

    def update(self, company):
        company.name = self.name.data
        company.email = self.email.data
        if self.password.data:
            company.password = self.password.data
        if company.detail:
            detail = company.detail
        else:
            detail = CompanyDetail()
            detail.user_id = company.id
        detail.site = self.site.data
        detail.description = self.description.data
        db.session.add(company)
        db.session.add(detail)
        db.session.commit()


class JobForm(FlaskForm):
    name = StringField('????')
    salary_low = IntegerField('????')
    salary_high = IntegerField('????')
    location = StringField('????')
    tags = StringField('????????,???')
    experience_requirement = SelectField(
        '????(?)',
        choices=[
            ('??', '??'),
            ('1', '1'),
            ('2', '2'),
            ('3', '3'),
            ('1-3', '1-3'),
            ('3-5', '3-5'),
            ('5+', '5+')
        ]
    )
    degree_requirement = SelectField(
        '????',
        choices=[
            ('??', '??'),
            ('??', '??'),
            ('??', '??'),
            ('??', '??'),
            ('??', '??')
        ]
    )
    description = TextAreaField('????', validators=[Length(0, 1500)])
    submit = SubmitField('??')

    def create_job(self, company):
        job = Job()
        self.populate_obj(job)
        job.company_id = company.id
        db.session.add(job)
        db.session.commit()
        return job

    def update_job(self, job):
        self.populate_obj(job)
        db.session.add(job)
        db.session.commit()
        return job
