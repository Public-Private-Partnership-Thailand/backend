"""
OC4IDS Serializers - Convert database models to OC4IDS JSON format
"""
from typing import Dict, Any


def project_to_oc4ids(project) -> Dict[str, Any]:
    """Convert Project model to OC4IDS JSON format"""
    
    result = {
        "id": str(project.id),
        "title": project.title,
        "description": project.description,
        "status": project.status,
        "purpose": project.purpose,
        "updated": project.updated_at.isoformat() if project.updated_at else None,
        "type": project.project_type.code if project.project_type else None,
        
        # Public Authority
        "publicAuthority": {
            "id": str(project.public_authority.id),
            "name": project.public_authority.name_en or project.public_authority.name_th
        } if project.public_authority else None,

        # Sectors
        "sector": [s.code for s in project.sectors],
        
        # Additional Classifications
        "additionalClassifications": [
            {
                "scheme": ac.scheme,
                "id": ac.code,
                "description": ac.description,
                "uri": ac.uri
            }
            for ac in project.additional_classifications
        ],
        
        # Locations
        "locations": [
            {
                "geometry": loc.geometry_coordinates, 
                "description": loc.description,
                "address": {
                    "streetAddress": loc.street_address,
                    "locality": loc.locality,
                    "region": loc.region,
                    "postalCode": loc.postal_code,
                    "countryName": loc.country_name
                },
                "gazetteers": [
                    {
                        "scheme": loc.gazetteer.scheme,
                        "identifiers": [
                            i.identifier for i in loc.gazetteer.identifiers
                        ]
                    }
                ] if loc.gazetteer else []
            } 
            for loc in project.locations_list
        ],

        # Parties
        "parties": [
            _serialize_party(p) for p in project.parties_list
        ],

        # Contracting Processes
        "contractingProcesses": [
            _serialize_contracting_process(cp) for cp in project.contracting_processes
        ],

        # Documents
        "documents": [
            {
                "id": d.local_id,
                "documentType": d.document_type,
                "title": d.title,
                "description": d.description,
                "url": d.url,
                "datePublished": d.date_published.isoformat() if d.date_published else None,
                "format": d.format,
                "author": d.author
            }
            for d in project.documents_list
        ],

        # Budget
        "budget": _serialize_budget(project.budget) if project.budget else None,
        
        # Identifiers
        "identifiers": [
            {
                "scheme": pid.scheme,
                "id": pid.identifier_value
            }
            for pid in project.identifiers_list
        ],

        # Related Projects
        "relatedProjects": [
            {
                "id": rp.identifier,
                "relationship": [rp.relationship],
                "title": rp.title,
                "scheme": rp.scheme,
                "uri": rp.uri
            }
            for rp in project.related_projects
        ],
        
        # Cost Measurements
        "costMeasurements": [
            _serialize_cost_measurement(cm) for cm in project.cost_measurements
        ],
        
        # Forecasts
        "forecasts": [
            _serialize_forecast(f) for f in project.forecasts
        ],
        
        # Metrics
        "metrics": [
            _serialize_metric(m) for m in project.metrics
        ],
        
        # Social
        "social": _serialize_social(project.social) if project.social else None,
        
        # Environment
        "environment": _serialize_environment(project.environment) if project.environment else None,
        
        # Benefits
        "benefits": [
            {
                "id": str(b.id),
                "title": b.title,
                "description": b.description,
                "beneficiaries": [
                    {
                        "description": ben.description,
                        "numberOfPeople": ben.number_of_people
                    } for ben in b.beneficiaries
                ]
            } for b in project.benefits
        ],
        
        # Completion
        "completion": {
            "endDate": project.completion.end_date.isoformat() if project.completion and project.completion.end_date else None,
            "finalScope": project.completion.final_scope,
            "finalValue": {
                "amount": project.completion.final_value_amount,
                "currency": project.completion.final_value_currency
            } if project.completion and project.completion.final_value_amount is not None else None
        } if project.completion else None,

        # Lobbying
        "lobbyingMeetings": [
            {
                "id": lb.local_id,
                "date": lb.meeting_date.isoformat() if lb.meeting_date else None,
                "numberOfParticipants": lb.number_of_participants,
                "address": {
                    "streetAddress": lb.street_address,
                    "locality": lb.locality,
                    "region": lb.region,
                    "postalCode": lb.postal_code,
                    "countryName": lb.country_name
                },
                "publicOffice": {
                    "name": lb.public_office_person_name,
                    "jobTitle": lb.public_office_job_title,
                    "organization": {
                        "name": lb.public_office_org_name,
                        "id": lb.public_office_org_id,
                    }
                }
            } for lb in project.lobbying_meetings
        ],

        # Policy Alignment
        "policyAlignment": {
            "policies": [p.policy for p in project.policy_alignment.policies],
            "description": project.policy_alignment.description 
        } if project.policy_alignment else None,

        # Asset Lifetime
        "assetLifetime": {
            "startDate": project.asset_lifetime.period_start_date.isoformat() if project.asset_lifetime.period_start_date else None,
            "endDate": project.asset_lifetime.period_end_date.isoformat() if project.asset_lifetime.period_end_date else None,
            "maxExtentDate": project.asset_lifetime.period_max_extent_date.isoformat() if project.asset_lifetime.period_max_extent_date else None,
            "durationInDays": project.asset_lifetime.period_duration_days
        } if project.asset_lifetime else None

    }
    
    # Process Periods - Map from DB rows back to OC4IDS fields
    period_map = {
        "duration": "period",
        "identification": "identificationPeriod",
        "preparation": "preparationPeriod",
        "implementation": "implementationPeriod",
        "completion": "completionPeriod",
        "maintenance": "maintenancePeriod",
        "decommissioning": "decommissioningPeriod",
        "assetLifetime": "assetLifetime"
    }
    
    for per in project.periods:
        field_name = period_map.get(per.period_type)
        if field_name:
            period_data = {
                "startDate": per.start_date.isoformat() if per.start_date else None,
                "endDate": per.end_date.isoformat() if per.end_date else None,
                "durationInDays": per.duration_days,
            }
            if per.max_extent_date:
                period_data["maxExtentDate"] = per.max_extent_date.isoformat()
            
            result[field_name] = period_data
            
    return result


def _serialize_party(p) -> Dict[str, Any]:
    """Serialize a Party to OC4IDS format"""
    return {
        "id": p.local_id,
        "name": p.name,
        "roles": [r.role for r in p.roles],
        "identifier": {
            "scheme": p.identifier_scheme,
            "id": p.identifier_value,
            "legalName": p.agency.name_th if p.agency else None,
            "uri": p.identifier_uri
        },
        "address": {
            "streetAddress": p.street_address,
            "locality": p.locality,
            "region": p.region,
            "postalCode": p.postal_code,
            "countryName": p.country_name
        },
        "contactPoint": {
            "name": p.contact_name,
            "email": p.contact_email,
            "telephone": p.contact_telephone,
            "fax": p.contact_fax,
            "url": p.contact_url
        },
        "additionalIdentifiers": [
            {
                "scheme": ai.scheme,
                "id": ai.identifier,
                "legalName": ai.ministry.name_th if ai.ministry else None,
                "uri": ai.uri
            }
            for ai in p.additional_identifiers
        ],
        "persons": [
            {
                "id": pp.local_id,
                "name": pp.name,
                "jobTitle": pp.job_title
            } for pp in p.people
        ],
        "beneficialOwners": [
            {
                "id": bo.local_id,
                "name": bo.name,
                "email": bo.email,
                "telephone": bo.telephone,
                "faxNumber": bo.fax_number,
                "identifier": {
                    "scheme": bo.identifier_scheme,
                    "id": bo.identifier_value
                },
                "address": {
                    "streetAddress": bo.street_address,
                    "locality": bo.locality,
                    "region": bo.region,
                    "postalCode": bo.postal_code,
                    "countryName": bo.country_name
                },
                "nationalities": [n.nationality for n in bo.nationalities]
            } for bo in p.beneficial_owners
        ],
        "classifications": [
            {
                "scheme": pc.scheme,
                "id": pc.classification_id
            } for pc in p.classifications
        ]
    }


def _serialize_contracting_process(cp) -> Dict[str, Any]:
    """Serialize a Contracting Process to OC4IDS format"""
    return {
        "id": cp.local_id,
        "summary": {
            "ocid": cp.ocid,
            "title": cp.title,
            "description": cp.description,
            "status": cp.status,
            "nature": cp.nature,
            "contractValue": {
                "amount": cp.contract_amount,
                "currency": cp.contract_currency
            },
            "contractPeriod": {
                "startDate": cp.period_start_date.isoformat() if cp.period_start_date else None,
                "endDate": cp.period_end_date.isoformat() if cp.period_end_date else None,
                "durationInDays": cp.period_duration_days
            },
            "tender": {
                "procurementMethod": cp.tender.procurement_method,
                "procurementMethodDetails": cp.tender.procurement_method_details,
                "datePublished": cp.tender.date_published.isoformat() if cp.tender.date_published else None,
                "numberOfTenderers": cp.tender.number_of_tenderers,
                "value": {
                    "amount": cp.tender.cost_estimate_amount,
                    "currency": cp.tender.cost_estimate_currency
                } if cp.tender else None,
                "tenderers": [
                    {
                        "id": t.local_id,
                        "name": t.name
                    } for t in cp.tender.tenderers
                ] if cp.tender else [],
                "procuringEntity": [
                    {
                        "name": e.name
                    } for e in cp.tender.tender_entities if e.role == "procuringEntity"
                ][0] if cp.tender and any(e.role == "procuringEntity" for e in cp.tender.tender_entities) else None,
                "sustainability": [
                    s.strategies for s in cp.tender.sustainability
                ] if cp.tender else []
            } if cp.tender else None,
            "suppliers": [
                {
                    "id": s.local_id,
                    "name": s.name
                } for s in cp.suppliers
            ],
            "social": {
                "description": cp.social.labor_description,
                "laborObligations": cp.social.labor_obligations,
                "laborBudget": {
                    "amount": cp.social.labor_budget_amount,
                    "currency": cp.social.labor_budget_currency
                }
            } if cp.social else None,
            "releases": [
                {
                    "id": r.local_id,
                    "date": r.date.isoformat() if r.date else None,
                    "tag": r.tag,
                    "url": r.url
                } for r in cp.releases
            ],
            "milestones": [
                {
                    "id": m.local_id,
                    "title": m.title,
                    "type": m.type,
                    "status": m.status,
                    "dueDate": m.due_date.isoformat() if m.due_date else None,
                    "dateMet": m.date_met.isoformat() if m.date_met else None,
                    "value": {
                        "amount": m.value_amount,
                        "currency": m.value_currency
                    } if m.value_amount is not None else None
                } for m in cp.milestones
            ],
            "transactions": [
                {
                    "id": t.local_id,
                    "source": t.source,
                    "date": t.date.isoformat() if t.date else None,
                    "value": {
                        "amount": t.amount,
                        "currency": t.currency
                    },
                    "payer": {"name": t.payer_name} if t.payer_name else None,
                    "payee": {"name": t.payee_name} if t.payee_name else None,
                    "uri": t.uri
                } for t in cp.transactions
            ],
            "modifications": [
                {
                    "id": mod.local_id,
                    "date": mod.date.isoformat() if mod.date else None,
                    "description": mod.description,
                    "rationale": mod.rationale,
                    "type": mod.type,
                    "releaseID": mod.release_id,
                    "contractValue": {
                        "originalAmount": {
                            "amount": mod.old_amount,
                            "currency": mod.old_currency
                        },
                        "amount": {
                            "amount": mod.new_amount,
                            "currency": mod.new_currency
                        }
                    } if mod.new_amount is not None else None
                } for mod in cp.modifications
            ],
            "documents": [
                {
                    "id": d.local_id,
                    "documentType": d.document_type,
                    "title": d.title,
                    "description": d.description,
                    "url": d.url,
                    "datePublished": d.date_published.isoformat() if d.date_published else None,
                    "format": d.format,
                    "language": d.language
                } for d in cp.documents
            ]
        }
    }


def _serialize_budget(budget) -> Dict[str, Any]:
    """Serialize Budget to OC4IDS format"""
    from oc4ids_datastore_api.utils import format_thai_amount
    
    return {
        "count": 0,
        "amount": {
            "amount": budget.total_amount,
            "currency": budget.currency,
            "amountFormatted": format_thai_amount(budget.total_amount) if budget.total_amount else ""
        },
        "approvalDate": budget.approval_date.isoformat() if budget.approval_date else None,
        "breakdown": [
            {
                "id": bd.local_id,
                "description": bd.description,
                "breakdown": [
                    {
                        "id": item.local_id,
                        "description": item.description,
                        "amount": {
                            "amount": item.amount,
                            "currency": item.currency
                        },
                        "period": {
                            "startDate": item.period_start_date.isoformat() if item.period_start_date else None,
                            "endDate": item.period_end_date.isoformat() if item.period_end_date else None
                        },
                        "sourceParty": {
                            "name": item.source_party_name,
                            "id": item.source_party_id
                        }
                    } for item in bd.items
                ]
            } for bd in budget.breakdowns
        ],
        "finance": [
            {
                "id": fin.local_id,
                "description": fin.description,
                "assetClass": fin.asset_class,
                "type": fin.type,
                "concessional": fin.concessional,
                "value": {
                    "amount": fin.value_amount,
                    "currency": fin.value_currency
                },
                "source": fin.source,
                "financingParty": {
                    "name": fin.financing_party_name,
                    "id": fin.financing_party_id
                },
                "interestRateMargin": fin.interest_rate_margin,
                "period": {
                    "startDate": fin.period_start_date.isoformat() if fin.period_start_date else None,
                    "endDate": fin.period_end_date.isoformat() if fin.period_end_date else None
                },
                "paymentPeriod": {
                    "startDate": fin.payment_period_start_date.isoformat() if fin.payment_period_start_date else None,
                    "endDate": fin.payment_period_end_date.isoformat() if fin.payment_period_end_date else None
                }
            } for fin in budget.finances
        ]
    }


def _serialize_cost_measurement(cm) -> Dict[str, Any]:
    """Serialize Cost Measurement to OC4IDS format"""
    return {
        "id": cm.local_id,
        "date": cm.measurement_date.isoformat() if cm.measurement_date else None,
        "lifeCycleCost": {
            "amount": cm.lifecycle_cost_amount,
            "currency": cm.lifecycle_cost_currency
        } if cm.lifecycle_cost_amount is not None else None,
        "costBreakdown": [
            {
                "id": cg.local_id,
                "description": cg.category,
                "breakdown": [
                    {
                        "id": ci.local_id,
                        "description": ci.classification_description,
                        "amount": {
                            "amount": ci.amount,
                            "currency": ci.currency
                        }
                    } for ci in cg.cost_items
                ]
            } for cg in cm.cost_groups
        ]
    }


def _serialize_forecast(f) -> Dict[str, Any]:
    """Serialize Forecast to OC4IDS format"""
    return {
        "id": f.local_id,
        "title": f.title,
        "description": f.description,
        "observations": [
            {
                "id": obs.local_id,
                "measure": obs.measure,
                "value": {
                    "amount": obs.value_amount,
                    "currency": obs.value_currency
                },
                "unit": {
                    "name": obs.unit_name,
                    "scheme": obs.unit_scheme,
                    "id": obs.unit_id
                },
                "period": {
                    "startDate": obs.period_start_date.isoformat() if obs.period_start_date else None,
                    "endDate": obs.period_end_date.isoformat() if obs.period_end_date else None
                }
            } for obs in f.observations
        ]
    }


def _serialize_metric(m) -> Dict[str, Any]:
    """Serialize Metric to OC4IDS format"""
    return {
        "id": m.local_id,
        "title": m.title,
        "description": m.description,
        "observations": [
            {
                "id": obs.local_id,
                "measure": obs.measure,
                "value": {
                    "amount": obs.value_amount,
                    "currency": obs.value_currency
                } if obs.value_amount is not None else None,
                "unit": {
                    "name": obs.unit_name
                } if obs.unit_name else None
            } for obs in m.observations
        ]
    }


def _serialize_social(social) -> Dict[str, Any]:
    """Serialize Social to OC4IDS format"""
    return {
        "inIndigenousLand": social.in_indigenous_land,
        "consultationMeetings": [
            {
                "id": m.local_id,
                "date": m.date.isoformat() if m.date else None,
                "numberOfParticipants": m.number_of_participants,
                "address": {
                    "streetAddress": m.street_address,
                    "locality": m.locality,
                    "region": m.region,
                    "postalCode": m.postal_code,
                    "countryName": m.country_name
                },
                "publicOffice": {
                    "person": {"name": m.person_name} if m.person_name else None,
                    "organization": {
                        "name": m.organization_name,
                        "id": m.organization_id
                    } if m.organization_name else None,
                    "jobTitle": m.job_title
                }
            } for m in social.consultation_meetings
        ],
        "landCompensationBudget": {
            "amount": social.land_compensation_amount,
            "currency": social.land_compensation_currency
        } if social.land_compensation_amount is not None else None,
        "healthAndSafety": {
            "materialTests": {
                "description": social.health_safety_material_test_description,
                "tests": [t.test for t in social.health_safety_tests]
            }
        }
    }


def _serialize_environment(env) -> Dict[str, Any]:
    """Serialize Environment to OC4IDS format"""
    return {
        "hasImpactAssessment": env.has_impact_assessment,
        "inProtectedArea": env.in_protected_area,
        "abatementCost": {
            "amount": env.abatement_cost_amount,
            "currency": env.abatement_cost_currency
        } if env.abatement_cost_amount is not None else None,
        "goals": [g.goal for g in env.goals],
        "climateOversightTypes": [c.oversight_type for c in env.climate_oversight_types],
        "conservationMeasures": [
            {
                "type": cm.type,
                "description": cm.description
            } for cm in env.conservation_measures
        ],
        "environmentalMeasures": [
            {
                "type": em.type,
                "description": em.description
            } for em in env.environmental_measures
        ],
        "climateMeasures": [
            {
                "type": cm.type.split(", ") if cm.type else [],
                "description": cm.description
            } for cm in env.climate_measures
        ],
        "impactCategories": [
            {
                "scheme": ic.scheme,
                "id": ic.category_id
            } for ic in env.impact_categories
        ]
    }
