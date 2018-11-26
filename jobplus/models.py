from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash


db = SQLAlchemy()


class Base(db.Model):
    """ ?? model ??????????????
    """
    # ?????????? Model ?
    __abstract__ = True
    # ??? defautl ? onupdate ???????????????
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime,
                           default=datetime.utcnow,
                           onupdate=datetime.utcnow)


user_job = db.Table(
    'user_job',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id', ondelete='CASCADE')),
    db.Column('job_id', db.Integer, db.ForeignKey('job.id', ondelete='CASCADE'))
)


class User(Base, UserMixin):
    __tablename__ = 'user'

    ROLE_USER = 10
    ROLE_COMPANY = 20
    ROLE_ADMIN = 30

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True, index=True, nullable=False)
    email = db.Column(db.String(64), unique=True, index=True, nullable=False)
    _password = db.Column('password', db.String(256), nullable=False)
    real_name = db.Column(db.String(20))
    phone = db.Column(db.String(11))
    work_years = db.Column(db.SmallInteger)
    role = db.Column(db.SmallInteger, default=ROLE_USER)
    # ??????????????????
    resume = db.relationship('Resume', uselist=False)
    collect_jobs = db.relationship('Job', secondary=user_job)
    # ?????????????
    resume_url = db.Column(db.String(64))

    # ??????
    detail = db.relationship('CompanyDetail', uselist=False)

    is_disable = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<User:{}>'.format(self.name)

    @property
    def enable_jobs(self):
        if not self.is_company:
            raise AttributeError('User has no attribute enable_jobs')
        return self.jobs.filter(Job.is_disable.is_(False))

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, orig_password):
        self._password = generate_password_hash(orig_password)

    def check_password(self, password):
        return check_password_hash(self._password, password)

    @property
    def is_admin(self):
        return self.role == self.ROLE_ADMIN

    @property
    def is_company(self):
        return self.role == self.ROLE_COMPANY

    @property
    def is_staff(self):
        return self.role == self.ROLE_USER


class Resume(Base):
    __tablename__ = 'resume'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', uselist=False)
    job_experiences = db.relationship('JobExperience')
    edu_experiences = db.relationship('EduExperience')
    project_experiences = db.relationship('ProjectExperience')

    def profile(self):
        pass


class Experience(Base):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    begin_at = db.Column(db.DateTime)
    end_at = db.Column(db.DateTime)
    # ?????????????????????????
    # ????????????????
    # ?????????????????????????
    description = db.Column(db.String(1024))


class JobExperience(Experience):
    __tablename__ = 'job_experience'

    company = db.Column(db.String(32), nullable=False)
    city = db.Column(db.String(32), nullable=False)
    resume_id = db.Column(db.Integer, db.ForeignKey('resume.id'))
    resume = db.relationship('Resume', uselist=False)


class EduExperience(Experience):
    __tablename__ = 'edu_experience'

    school = db.Column(db.String(32), nullable=False)
    # ????
    specialty = db.Column(db.String(32), nullable=False)
    degree = db.Column(db.String(16))
    resume_id = db.Column(db.Integer, db.ForeignKey('resume.id'))
    resume = db.relationship('Resume', uselist=False)


class ProjectExperience(Experience):
    __tablename__ = 'preject_experience'

    name = db.Column(db.String(32), nullable=False)
    # ?????????
    role = db.Column(db.String(32))
    # ?????????
    technologys = db.Column(db.String(64))
    resume_id = db.Column(db.Integer, db.ForeignKey('resume.id'))
    resume = db.relationship('Resume', uselist=False)


class CompanyDetail(Base):
    __tablename__ = 'company_detail'

    id = db.Column(db.Integer, primary_key=True)
    logo = db.Column(db.String(256), nullable=False)
    site = db.Column(db.String(128), nullable=False)
    location = db.Column(db.String(24), nullable=False)
    # ?????
    description = db.Column(db.String(100))
    # ???????????
    about = db.Column(db.String(1024))
    # ?????????????????10?
    tags = db.Column(db.String(128))
    # ??????????????????10?
    stack = db.Column(db.String(128))
    # ????
    team_introduction = db.Column(db.String(256))
    # ????????????????? 10 ?
    welfares = db.Column(db.String(256))
    # ????
    field = db.Column(db.String(128))
    # ????
    finance_stage = db.Column(db.String(128))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='SET NULL'))
    user = db.relationship('User', uselist=False, backref=db.backref('company_detail', uselist=False))

    def __repr__(self):
        return '<CompanyDetail {}>'.format(self.id)


class Job(Base):
    __tablename__ = 'job'

    id = db.Column(db.Integer, primary_key=True)
    # ????
    name = db.Column(db.String(24))
    salary_low = db.Column(db.Integer, nullable=False)
    salary_high = db.Column(db.Integer, nullable=False)
    location = db.Column(db.String(24))
    description = db.Column(db.String(1500))
    # ?????????????????10?
    tags = db.Column(db.String(128))
    experience_requirement = db.Column(db.String(32))
    degree_requirement = db.Column(db.String(32))
    is_fulltime = db.Column(db.Boolean, default=True)
    # ?????
    is_open = db.Column(db.Boolean, default=True)
    company_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    company = db.relationship('User', uselist=False, backref=db.backref('jobs', lazy='dynamic'))
    views_count = db.Column(db.Integer, default=0)
    is_disable = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<Job {}>'.format(self.name)

    @property
    def tag_list(self):
        return self.tags.split(',')

    @property
    def current_user_is_applied(self):
        d = Delivery.query.filter_by(job_id=self.id, user_id=current_user.id).first()
        return (d is not None)


class Delivery(Base):
    __tablename__ = 'delivery'

    # ??????
    STATUS_WAITING = 1
    # ???
    STATUS_REJECT = 2
    # ??????????
    STATUS_ACCEPT = 3

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id', ondelete='SET NULL'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='SET NULL'))
    company_id = db.Column(db.Integer)
    status = db.Column(db.SmallInteger, default=STATUS_WAITING)
    # ????
    response = db.Column(db.String(256))

    @property
    def user(self):
        return User.query.get(self.user_id)

    @property
    def job(self):
        return Job.query.get(self.job_id)
