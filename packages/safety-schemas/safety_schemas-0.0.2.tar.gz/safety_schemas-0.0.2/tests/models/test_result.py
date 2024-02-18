from safety_schemas.models.package import PythonDependency
from safety_schemas.models.result import DependencyResultModel
from safety_schemas.models import PythonSpecification
from safety_schemas.models.vulnerability import Vulnerability

def test_dependency_result_model():
    # Create sample data for testing
    dependencies = [
        PythonDependency(
            name="dependency1",
            version="1.0.0",
            specifications=[
                PythonSpecification(
                    name="spec1",
                    vulnerabilities=[
                        Vulnerability(id="CVE-2021-1234", severity="High"),
                        Vulnerability(id="CVE-2021-5678", severity="Medium"),
                    ],
                ),
                PythonSpecification(
                    name="spec2",
                    vulnerabilities=[
                        Vulnerability(id="CVE-2021-9012", severity="Low"),
                    ],
                ),
            ],
        ),
        PythonDependency(
            name="dependency2",
            version="2.0.0",
            specifications=[
                PythonSpecification(
                    name="spec3",
                    vulnerabilities=[
                        Vulnerability(id="CVE-2021-3456", severity="Critical"),
                    ],
                ),
            ],
        ),
    ]

    result_model = DependencyResultModel(dependencies=dependencies)

    affected_specifications = result_model.get_affected_specifications(include_ignored=False)
    assert len(affected_specifications) == 3

    affected_specifications_with_ignored = result_model.get_affected_specifications(include_ignored=True)
    assert len(affected_specifications_with_ignored) == 4


    affected_dependencies = result_model.get_affected_dependencies()
    assert len(affected_dependencies) == 2
