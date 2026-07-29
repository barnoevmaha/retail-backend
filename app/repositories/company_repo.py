from sqlalchemy.orm import Session

from app.models.company import Company


class CompanyRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self) -> Company | None:
        return self.db.query(Company).first()

    def upsert(self, **kwargs) -> Company:
        company = self.db.query(Company).first()
        if company:
            for k, v in kwargs.items():
                setattr(company, k, v)
        else:
            company = Company(**kwargs)
            self.db.add(company)
        self.db.commit()
        self.db.refresh(company)
        return company
