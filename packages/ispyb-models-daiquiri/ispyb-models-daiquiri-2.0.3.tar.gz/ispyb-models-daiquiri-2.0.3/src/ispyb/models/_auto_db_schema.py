# coding: utf-8
from sqlalchemy import (
    BINARY,
    Column,
    Computed,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    String,
    TIMESTAMP,
    Table,
    Text,
    Time,
    text,
)
from sqlalchemy.dialects.mysql import (
    INTEGER,
    LONGBLOB,
    LONGTEXT,
    MEDIUMINT,
    SMALLINT,
    TINYINT,
    TINYTEXT,
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from .base import CustomBase


Base = declarative_base(cls=CustomBase)
metadata = Base.metadata


class AdminActivity(Base):
    __tablename__ = "AdminActivity"

    adminActivityId = Column(INTEGER(11), primary_key=True)
    username = Column(
        String(45), nullable=False, unique=True, server_default=text("''")
    )
    action = Column(String(45), index=True)
    comments = Column(String(100))
    dateTime = Column(DateTime)


class AdminVar(Base):
    __tablename__ = "AdminVar"
    __table_args__ = {"comment": "ISPyB administration values"}

    varId = Column(INTEGER(11), primary_key=True)
    name = Column(String(32), index=True)
    value = Column(String(1024), index=True)


class AutoProc(Base):
    __tablename__ = "AutoProc"
    __table_args__ = (
        Index(
            "AutoProc_refined_unit_cell",
            "refinedCell_a",
            "refinedCell_b",
            "refinedCell_c",
            "refinedCell_alpha",
            "refinedCell_beta",
            "refinedCell_gamma",
            "spaceGroup",
        ),
    )

    autoProcId = Column(
        INTEGER(10), primary_key=True, comment="Primary key (auto-incremented)"
    )
    autoProcProgramId = Column(INTEGER(10), index=True, comment="Related program item")
    spaceGroup = Column(String(45), comment="Space group")
    refinedCell_a = Column(Float, comment="Refined cell")
    refinedCell_b = Column(Float, comment="Refined cell")
    refinedCell_c = Column(Float, comment="Refined cell")
    refinedCell_alpha = Column(Float, comment="Refined cell")
    refinedCell_beta = Column(Float, comment="Refined cell")
    refinedCell_gamma = Column(Float, comment="Refined cell")
    recordTimeStamp = Column(DateTime, comment="Creation or last update date/time")


class BeamCalendar(Base):
    __tablename__ = "BeamCalendar"

    beamCalendarId = Column(INTEGER(10), primary_key=True)
    run = Column(String(7), nullable=False)
    beamStatus = Column(String(24), nullable=False)
    startDate = Column(DateTime, nullable=False)
    endDate = Column(DateTime, nullable=False)


class ComponentType(Base):
    __tablename__ = "ComponentType"

    componentTypeId = Column(INTEGER(11), primary_key=True)
    name = Column(String(31), nullable=False)


class ConcentrationType(Base):
    __tablename__ = "ConcentrationType"

    concentrationTypeId = Column(INTEGER(11), primary_key=True)
    name = Column(String(31), nullable=False)
    symbol = Column(String(8), nullable=False)
    proposalType = Column(String(10))
    active = Column(
        TINYINT(1), server_default=text("1"), comment="1=active, 0=inactive"
    )


class ContainerType(Base):
    __tablename__ = "ContainerType"
    __table_args__ = {"comment": "A lookup table for different types of containers"}

    containerTypeId = Column(INTEGER(10), primary_key=True)
    name = Column(String(100))
    proposalType = Column(String(10))
    active = Column(
        TINYINT(1), server_default=text("1"), comment="1=active, 0=inactive"
    )
    capacity = Column(INTEGER(11))
    wellPerRow = Column(SMALLINT(6))
    dropPerWellX = Column(SMALLINT(6))
    dropPerWellY = Column(SMALLINT(6))
    dropHeight = Column(Float)
    dropWidth = Column(Float)
    dropOffsetX = Column(Float)
    dropOffsetY = Column(Float)
    wellDrop = Column(SMALLINT(6))


class Detector(Base):
    __tablename__ = "Detector"
    __table_args__ = (
        Index(
            "Detector_FKIndex1",
            "detectorType",
            "detectorManufacturer",
            "detectorModel",
            "detectorPixelSizeHorizontal",
            "detectorPixelSizeVertical",
        ),
        {"comment": "Detector table is linked to a dataCollection"},
    )

    detectorId = Column(
        INTEGER(11), primary_key=True, comment="Primary key (auto-incremented)"
    )
    detectorType = Column(String(255))
    detectorManufacturer = Column(String(255))
    detectorModel = Column(String(255))
    detectorPixelSizeHorizontal = Column(Float)
    detectorPixelSizeVertical = Column(Float)
    DETECTORMAXRESOLUTION = Column(Float)
    DETECTORMINRESOLUTION = Column(Float)
    detectorSerialNumber = Column(String(30), unique=True)
    detectorDistanceMin = Column(Float(asdecimal=True))
    detectorDistanceMax = Column(Float(asdecimal=True))
    trustedPixelValueRangeLower = Column(Float(asdecimal=True))
    trustedPixelValueRangeUpper = Column(Float(asdecimal=True))
    sensorThickness = Column(Float)
    overload = Column(Float)
    XGeoCorr = Column(String(255))
    YGeoCorr = Column(String(255))
    detectorMode = Column(String(255))
    density = Column(Float)
    composition = Column(String(16))
    numberOfPixelsX = Column(MEDIUMINT(9), comment="Detector number of pixels in x")
    numberOfPixelsY = Column(MEDIUMINT(9), comment="Detector number of pixels in y")
    detectorRollMin = Column(Float(asdecimal=True), comment="unit: degrees")
    detectorRollMax = Column(Float(asdecimal=True), comment="unit: degrees")
    localName = Column(String(40), comment="Colloquial name for the detector")


class ExperimentType(Base):
    __tablename__ = "ExperimentType"
    __table_args__ = {"comment": "A lookup table for different types of experients"}

    experimentTypeId = Column(INTEGER(10), primary_key=True)
    name = Column(String(100))
    proposalType = Column(String(10))
    active = Column(
        TINYINT(1), server_default=text("1"), comment="1=active, 0=inactive"
    )


class ImageQualityIndicators(Base):
    __tablename__ = "ImageQualityIndicators"

    dataCollectionId = Column(INTEGER(11), primary_key=True, nullable=False)
    imageNumber = Column(MEDIUMINT(8), primary_key=True, nullable=False)
    imageId = Column(INTEGER(12))
    autoProcProgramId = Column(
        INTEGER(10), comment="Foreign key to the AutoProcProgram table"
    )
    spotTotal = Column(INTEGER(10), comment="Total number of spots")
    inResTotal = Column(
        INTEGER(10), comment="Total number of spots in resolution range"
    )
    goodBraggCandidates = Column(
        INTEGER(10), comment="Total number of Bragg diffraction spots"
    )
    iceRings = Column(INTEGER(10), comment="Number of ice rings identified")
    method1Res = Column(Float, comment="Resolution estimate 1 (see publication)")
    method2Res = Column(Float, comment="Resolution estimate 2 (see publication)")
    maxUnitCell = Column(
        Float, comment="Estimation of the largest possible unit cell edge"
    )
    pctSaturationTop50Peaks = Column(
        Float, comment="The fraction of the dynamic range being used"
    )
    inResolutionOvrlSpots = Column(INTEGER(10), comment="Number of spots overloaded")
    binPopCutOffMethod2Res = Column(
        Float, comment="Cut off used in resolution limit calculation"
    )
    recordTimeStamp = Column(DateTime, comment="Creation or last update date/time")
    totalIntegratedSignal = Column(Float(asdecimal=True))
    dozor_score = Column(Float(asdecimal=True), comment="dozor_score")
    driftFactor = Column(Float, comment="EM movie drift factor")


class InspectionType(Base):
    __tablename__ = "InspectionType"

    inspectionTypeId = Column(INTEGER(11), primary_key=True)
    name = Column(String(45))


class Laboratory(Base):
    __tablename__ = "Laboratory"

    laboratoryId = Column(INTEGER(10), primary_key=True)
    laboratoryUUID = Column(String(45))
    name = Column(String(45))
    address = Column(String(255))
    city = Column(String(45))
    country = Column(String(45))
    url = Column(String(255))
    organization = Column(String(45))
    recordTimeStamp = Column(
        TIMESTAMP,
        nullable=False,
        server_default=text("current_timestamp()"),
        comment="Creation or last update date/time",
    )
    laboratoryPk = Column(INTEGER(10))
    postcode = Column(String(15))


class Permission(Base):
    __tablename__ = "Permission"

    permissionId = Column(INTEGER(11), primary_key=True)
    type = Column(String(15), nullable=False)
    description = Column(String(100))

    UserGroup = relationship("UserGroup", secondary="UserGroup_has_Permission")


class Position(Base):
    __tablename__ = "Position"

    positionId = Column(
        INTEGER(11), primary_key=True, comment="Primary key (auto-incremented)"
    )
    relativePositionId = Column(
        ForeignKey("Position.positionId", ondelete="CASCADE", onupdate="CASCADE"),
        index=True,
        comment="relative position, null otherwise",
    )
    posX = Column(Float(asdecimal=True))
    posY = Column(Float(asdecimal=True))
    posZ = Column(Float(asdecimal=True))
    scale = Column(Float(asdecimal=True))
    recordTimeStamp = Column(DateTime, comment="Creation or last update date/time")
    X = Column(Float(asdecimal=True), Computed("(`posX`)", persisted=False))
    Y = Column(Float(asdecimal=True), Computed("(`posY`)", persisted=False))
    Z = Column(Float(asdecimal=True), Computed("(`posZ`)", persisted=False))

    parent = relationship("Position", remote_side=[positionId])


class Positioner(Base):
    __tablename__ = "Positioner"
    __table_args__ = {
        "comment": "An arbitrary positioner and its value, could be e.g. a motor. Allows for instance to store some positions with a sample or subsample"
    }

    positionerId = Column(INTEGER(10), primary_key=True)
    positioner = Column(String(50), nullable=False)
    value = Column(Float, nullable=False)


class SchemaStatus(Base):
    __tablename__ = "SchemaStatus"

    schemaStatusId = Column(INTEGER(11), primary_key=True)
    scriptName = Column(String(100), nullable=False, unique=True)
    schemaStatus = Column(String(10))
    recordTimeStamp = Column(
        TIMESTAMP, nullable=False, server_default=text("current_timestamp()")
    )


class UserGroup(Base):
    __tablename__ = "UserGroup"

    userGroupId = Column(INTEGER(11), primary_key=True)
    name = Column(String(31), nullable=False, unique=True)


class Workflow(Base):
    __tablename__ = "Workflow"

    workflowId = Column(
        INTEGER(11), primary_key=True, comment="Primary key (auto-incremented)"
    )
    workflowTitle = Column(String(255))
    workflowType = Column(
        Enum(
            "Undefined",
            "BioSAXS Post Processing",
            "EnhancedCharacterisation",
            "LineScan",
            "MeshScan",
            "Dehydration",
            "KappaReorientation",
            "BurnStrategy",
            "XrayCentering",
            "DiffractionTomography",
            "TroubleShooting",
            "VisualReorientation",
            "HelicalCharacterisation",
            "GroupedProcessing",
            "MXPressE",
            "MXPressO",
            "MXPressL",
            "MXScore",
            "MXPressI",
            "MXPressM",
            "MXPressA",
        )
    )
    workflowTypeId = Column(INTEGER(11))
    comments = Column(String(1024))
    status = Column(String(255))
    resultFilePath = Column(String(255))
    logFilePath = Column(String(255))
    recordTimeStamp = Column(DateTime, comment="Creation or last update date/time")
    workflowDescriptionFullPath = Column(
        String(255), comment="Full file path to a json description of the workflow"
    )


class WorkflowType(Base):
    __tablename__ = "WorkflowType"

    workflowTypeId = Column(INTEGER(11), primary_key=True)
    workflowTypeName = Column(String(45))
    comments = Column(String(2048))
    recordTimeStamp = Column(TIMESTAMP)


class VRun(Base):
    __tablename__ = "v_run"
    __table_args__ = (Index("v_run_idx1", "startDate", "endDate"),)

    runId = Column(INTEGER(11), primary_key=True)
    run = Column(String(7), nullable=False, server_default=text("''"))
    startDate = Column(DateTime)
    endDate = Column(DateTime)


class AutoProcScaling(Base):
    __tablename__ = "AutoProcScaling"
    __table_args__ = (Index("AutoProcScalingIdx1", "autoProcScalingId", "autoProcId"),)

    autoProcScalingId = Column(
        INTEGER(10), primary_key=True, comment="Primary key (auto-incremented)"
    )
    autoProcId = Column(
        ForeignKey("AutoProc.autoProcId", ondelete="CASCADE", onupdate="CASCADE"),
        index=True,
        comment="Related autoProc item (used by foreign key)",
    )
    recordTimeStamp = Column(DateTime, comment="Creation or last update date/time")

    AutoProc = relationship("AutoProc")


class BeamLineSetup(Base):
    __tablename__ = "BeamLineSetup"

    beamLineSetupId = Column(INTEGER(10), primary_key=True)
    detectorId = Column(ForeignKey("Detector.detectorId"), index=True)
    synchrotronMode = Column(String(255))
    undulatorType1 = Column(String(45))
    undulatorType2 = Column(String(45))
    undulatorType3 = Column(String(45))
    focalSpotSizeAtSample = Column(Float)
    focusingOptic = Column(String(255))
    beamDivergenceHorizontal = Column(Float)
    beamDivergenceVertical = Column(Float)
    polarisation = Column(Float)
    monochromatorType = Column(String(255))
    setupDate = Column(DateTime)
    synchrotronName = Column(String(255))
    maxExpTimePerDataCollection = Column(Float(asdecimal=True))
    maxExposureTimePerImage = Column(Float, comment="unit: seconds")
    minExposureTimePerImage = Column(Float(asdecimal=True))
    goniostatMaxOscillationSpeed = Column(Float(asdecimal=True))
    goniostatMaxOscillationWidth = Column(
        Float(asdecimal=True), comment="unit: degrees"
    )
    goniostatMinOscillationWidth = Column(Float(asdecimal=True))
    maxTransmission = Column(Float(asdecimal=True), comment="unit: percentage")
    minTransmission = Column(Float(asdecimal=True))
    recordTimeStamp = Column(
        TIMESTAMP,
        nullable=False,
        server_default=text("current_timestamp()"),
        comment="Creation or last update date/time",
    )
    CS = Column(Float, comment="Spherical Aberration, Units: mm?")
    beamlineName = Column(String(50), comment="Beamline that this setup relates to")
    beamSizeXMin = Column(Float, comment="unit: um")
    beamSizeXMax = Column(Float, comment="unit: um")
    beamSizeYMin = Column(Float, comment="unit: um")
    beamSizeYMax = Column(Float, comment="unit: um")
    energyMin = Column(Float, comment="unit: eV")
    energyMax = Column(Float, comment="unit: eV")
    omegaMin = Column(Float, comment="unit: degrees")
    omegaMax = Column(Float, comment="unit: degrees")
    kappaMin = Column(Float, comment="unit: degrees")
    kappaMax = Column(Float, comment="unit: degrees")
    phiMin = Column(Float, comment="unit: degrees")
    phiMax = Column(Float, comment="unit: degrees")
    active = Column(TINYINT(1), nullable=False, server_default=text("0"))
    numberOfImagesMax = Column(MEDIUMINT(8))
    numberOfImagesMin = Column(MEDIUMINT(8))
    boxSizeXMin = Column(Float(asdecimal=True), comment="For gridscans, unit: um")
    boxSizeXMax = Column(Float(asdecimal=True), comment="For gridscans, unit: um")
    boxSizeYMin = Column(Float(asdecimal=True), comment="For gridscans, unit: um")
    boxSizeYMax = Column(Float(asdecimal=True), comment="For gridscans, unit: um")
    monoBandwidthMin = Column(Float(asdecimal=True), comment="unit: percentage")
    monoBandwidthMax = Column(Float(asdecimal=True), comment="unit: percentage")
    preferredDataCentre = Column(
        String(30),
        comment="Relevant datacentre to use to process data from this beamline",
    )
    amplitudeContrast = Column(Float, comment="Needed for cryo-ET")

    Detector = relationship("Detector")


class DiffractionPlan(Base):
    __tablename__ = "DiffractionPlan"

    diffractionPlanId = Column(INTEGER(10), primary_key=True)
    name = Column(String(20))
    experimentKind = Column(
        Enum(
            "Default",
            "MXPressE",
            "MXPressO",
            "MXPressE_SAD",
            "MXScore",
            "MXPressM",
            "MAD",
            "SAD",
            "Fixed",
            "Ligand binding",
            "Refinement",
            "OSC",
            "MAD - Inverse Beam",
            "SAD - Inverse Beam",
            "MESH",
            "XFE",
            "Stepped transmission",
            "XChem High Symmetry",
            "XChem Low Symmetry",
            "Commissioning",
        )
    )
    exposureTime = Column(Float)
    comments = Column(String(1024))
    recordTimeStamp = Column(
        TIMESTAMP,
        nullable=False,
        server_default=text("current_timestamp()"),
        comment="Creation or last update date/time",
    )
    monochromator = Column(String(8), comment="DMM or DCM")
    energy = Column(Float, comment="eV")
    transmission = Column(Float, comment="Decimal fraction in range [0,1]")
    boxSizeX = Column(Float, comment="microns")
    boxSizeY = Column(Float, comment="microns")
    detectorId = Column(
        ForeignKey("Detector.detectorId", onupdate="CASCADE"), index=True
    )
    monoBandwidth = Column(Float(asdecimal=True))
    userPath = Column(
        String(100),
        comment='User-specified relative "root" path inside the session directory to be used for holding collected data',
    )
    experimentTypeId = Column(ForeignKey("ExperimentType.experimentTypeId"), index=True)
    collectionMode = Column(
        Enum("auto", "manual"),
        comment="The requested collection mode, possible values are auto, manual",
    )
    priority = Column(
        INTEGER(4),
        comment="The priority of this sample relative to others in the shipment",
    )
    scanParameters = Column(
        LONGTEXT,
        comment="JSON serialised scan parameters, useful for parameters without designated columns",
    )

    Detector = relationship("Detector")
    ExperimentType = relationship("ExperimentType")


class Person(Base):
    __tablename__ = "Person"

    personId = Column(INTEGER(10), primary_key=True)
    laboratoryId = Column(ForeignKey("Laboratory.laboratoryId"), index=True)
    siteId = Column(INTEGER(11), index=True)
    personUUID = Column(String(45))
    familyName = Column(String(100), index=True)
    givenName = Column(String(45))
    title = Column(String(45))
    emailAddress = Column(String(60))
    phoneNumber = Column(String(45))
    login = Column(String(45), unique=True)
    faxNumber = Column(String(45))
    recordTimeStamp = Column(
        TIMESTAMP,
        nullable=False,
        server_default=text("current_timestamp()"),
        comment="Creation or last update date/time",
    )
    cache = Column(Text)
    externalId = Column(BINARY(16))

    Laboratory = relationship("Laboratory")
    UserGroup = relationship("UserGroup", secondary="UserGroup_has_Person")


t_UserGroup_has_Permission = Table(
    "UserGroup_has_Permission",
    metadata,
    Column(
        "userGroupId",
        ForeignKey("UserGroup.userGroupId", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
        nullable=False,
    ),
    Column(
        "permissionId",
        ForeignKey("Permission.permissionId", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
        nullable=False,
        index=True,
    ),
)


class WorkflowStep(Base):
    __tablename__ = "WorkflowStep"

    workflowStepId = Column(INTEGER(11), primary_key=True)
    workflowId = Column(ForeignKey("Workflow.workflowId"), nullable=False, index=True)
    type = Column(String(45))
    status = Column(String(45))
    folderPath = Column(String(1024))
    imageResultFilePath = Column(String(1024))
    htmlResultFilePath = Column(String(1024))
    resultFilePath = Column(String(1024))
    comments = Column(String(2048))
    crystalSizeX = Column(String(45))
    crystalSizeY = Column(String(45))
    crystalSizeZ = Column(String(45))
    maxDozorScore = Column(String(45))
    recordTimeStamp = Column(TIMESTAMP)

    Workflow = relationship("Workflow")


class AutoProcScalingStatistics(Base):
    __tablename__ = "AutoProcScalingStatistics"
    __table_args__ = (
        Index(
            "AutoProcScalingStatistics_scalingId_statisticsType",
            "autoProcScalingId",
            "scalingStatisticsType",
        ),
    )

    autoProcScalingStatisticsId = Column(
        INTEGER(10), primary_key=True, comment="Primary key (auto-incremented)"
    )
    autoProcScalingId = Column(
        ForeignKey(
            "AutoProcScaling.autoProcScalingId", ondelete="CASCADE", onupdate="CASCADE"
        ),
        comment="Related autoProcScaling item (used by foreign key)",
    )
    scalingStatisticsType = Column(
        Enum("overall", "innerShell", "outerShell"),
        nullable=False,
        index=True,
        server_default=text("'overall'"),
        comment="Scaling statistics type",
    )
    comments = Column(String(255), comment="Comments...")
    resolutionLimitLow = Column(Float, comment="Low resolution limit")
    resolutionLimitHigh = Column(Float, comment="High resolution limit")
    rMerge = Column(Float, comment="Rmerge")
    rMeasWithinIPlusIMinus = Column(Float, comment="Rmeas (within I+/I-)")
    rMeasAllIPlusIMinus = Column(Float, comment="Rmeas (all I+ & I-)")
    rPimWithinIPlusIMinus = Column(Float, comment="Rpim (within I+/I-) ")
    rPimAllIPlusIMinus = Column(Float, comment="Rpim (all I+ & I-)")
    fractionalPartialBias = Column(Float, comment="Fractional partial bias")
    nTotalObservations = Column(INTEGER(10), comment="Total number of observations")
    nTotalUniqueObservations = Column(INTEGER(10), comment="Total number unique")
    meanIOverSigI = Column(Float, comment="Mean((I)/sd(I))")
    completeness = Column(Float, comment="Completeness")
    multiplicity = Column(Float, comment="Multiplicity")
    anomalousCompleteness = Column(Float, comment="Anomalous completeness")
    anomalousMultiplicity = Column(Float, comment="Anomalous multiplicity")
    recordTimeStamp = Column(DateTime, comment="Creation or last update date/time")
    anomalous = Column(
        TINYINT(1), server_default=text("0"), comment="boolean type:0 noanoum - 1 anoum"
    )
    ccHalf = Column(Float, comment="information from XDS")
    ccAnomalous = Column(Float)
    resIOverSigI2 = Column(Float, comment="Resolution where I/Sigma(I) equals 2")

    AutoProcScaling = relationship("AutoProcScaling")


class DataCollectionPlanHasDetector(Base):
    __tablename__ = "DataCollectionPlan_has_Detector"
    __table_args__ = (
        Index(
            "dataCollectionPlanId", "dataCollectionPlanId", "detectorId", unique=True
        ),
    )

    dataCollectionPlanHasDetectorId = Column(INTEGER(11), primary_key=True)
    dataCollectionPlanId = Column(
        ForeignKey("DiffractionPlan.diffractionPlanId"), nullable=False
    )
    detectorId = Column(ForeignKey("Detector.detectorId"), nullable=False, index=True)
    exposureTime = Column(Float(asdecimal=True))
    distance = Column(Float(asdecimal=True))
    roll = Column(Float(asdecimal=True))

    DiffractionPlan = relationship("DiffractionPlan")
    Detector = relationship("Detector")


class Proposal(Base):
    __tablename__ = "Proposal"
    __table_args__ = (
        Index(
            "Proposal_FKIndexCodeNumber", "proposalCode", "proposalNumber", unique=True
        ),
    )

    proposalId = Column(INTEGER(10), primary_key=True)
    personId = Column(
        ForeignKey("Person.personId", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
        server_default=text("0"),
    )
    title = Column(String(200))
    proposalCode = Column(String(45))
    proposalNumber = Column(String(45))
    bltimeStamp = Column(
        TIMESTAMP, nullable=False, server_default=text("current_timestamp()")
    )
    proposalType = Column(String(2), comment="Proposal type: MX, BX")
    externalId = Column(BINARY(16))
    state = Column(Enum("Open", "Closed", "Cancelled"), server_default=text("'Open'"))

    Person = relationship("Person")


t_UserGroup_has_Person = Table(
    "UserGroup_has_Person",
    metadata,
    Column(
        "userGroupId",
        ForeignKey("UserGroup.userGroupId", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
        nullable=False,
    ),
    Column(
        "personId",
        ForeignKey("Person.personId", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
        nullable=False,
        index=True,
    ),
)


class BLSession(Base):
    __tablename__ = "BLSession"
    __table_args__ = (Index("proposalId", "proposalId", "visit_number", unique=True),)

    sessionId = Column(INTEGER(10), primary_key=True)
    beamLineSetupId = Column(
        ForeignKey(
            "BeamLineSetup.beamLineSetupId", ondelete="CASCADE", onupdate="CASCADE"
        ),
        index=True,
    )
    proposalId = Column(
        ForeignKey("Proposal.proposalId", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        server_default=text("0"),
    )
    beamCalendarId = Column(ForeignKey("BeamCalendar.beamCalendarId"), index=True)
    startDate = Column(DateTime, index=True)
    endDate = Column(DateTime, index=True)
    beamLineName = Column(String(45), index=True)
    scheduled = Column(TINYINT(1))
    nbShifts = Column(INTEGER(10))
    comments = Column(String(2000))
    beamLineOperator = Column(String(45))
    bltimeStamp = Column(
        TIMESTAMP, nullable=False, server_default=text("current_timestamp()")
    )
    visit_number = Column(INTEGER(10), server_default=text("0"))
    sessionTitle = Column(String(255), comment="fx accounts only")
    externalId = Column(BINARY(16))
    archived = Column(
        TINYINT(1),
        server_default=text("0"),
        comment="The data for the session is archived and no longer available on disk",
    )

    BeamCalendar = relationship("BeamCalendar")
    BeamLineSetup = relationship("BeamLineSetup")
    Proposal = relationship("Proposal")


class LabContact(Base):
    __tablename__ = "LabContact"
    __table_args__ = (
        Index("personAndProposal", "personId", "proposalId", unique=True),
        Index("cardNameAndProposal", "cardName", "proposalId", unique=True),
    )

    labContactId = Column(INTEGER(10), primary_key=True)
    personId = Column(
        ForeignKey("Person.personId", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    cardName = Column(String(40), nullable=False)
    proposalId = Column(
        ForeignKey("Proposal.proposalId", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    defaultCourrierCompany = Column(String(45))
    courierAccount = Column(String(45))
    billingReference = Column(String(45))
    dewarAvgCustomsValue = Column(INTEGER(10), nullable=False, server_default=text("0"))
    dewarAvgTransportValue = Column(
        INTEGER(10), nullable=False, server_default=text("0")
    )
    recordTimeStamp = Column(
        TIMESTAMP,
        nullable=False,
        server_default=text("current_timestamp()"),
        comment="Creation or last update date/time",
    )

    Person = relationship("Person")
    Proposal = relationship("Proposal")


class ProposalHasPerson(Base):
    __tablename__ = "ProposalHasPerson"

    proposalHasPersonId = Column(INTEGER(10), primary_key=True)
    proposalId = Column(ForeignKey("Proposal.proposalId"), nullable=False, index=True)
    personId = Column(ForeignKey("Person.personId"), nullable=False, index=True)
    role = Column(
        Enum(
            "Co-Investigator",
            "Principal Investigator",
            "Alternate Contact",
            "ERA Admin",
            "Associate",
        )
    )

    Person = relationship("Person")
    Proposal = relationship("Proposal")


class Protein(Base):
    __tablename__ = "Protein"
    __table_args__ = (Index("ProteinAcronym_Index", "proposalId", "acronym"),)

    proteinId = Column(INTEGER(10), primary_key=True)
    proposalId = Column(
        ForeignKey("Proposal.proposalId", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        server_default=text("0"),
    )
    name = Column(String(255))
    acronym = Column(String(45), index=True)
    description = Column(
        Text, comment="A description/summary using words and sentences"
    )
    hazardGroup = Column(
        TINYINT(3),
        nullable=False,
        server_default=text("1"),
        comment="A.k.a. risk group",
    )
    containmentLevel = Column(
        TINYINT(3),
        nullable=False,
        server_default=text("1"),
        comment="A.k.a. biosafety level, which indicates the level of containment required",
    )
    safetyLevel = Column(Enum("GREEN", "YELLOW", "RED"))
    molecularMass = Column(Float(asdecimal=True))
    bltimeStamp = Column(
        TIMESTAMP, nullable=False, server_default=text("current_timestamp()")
    )
    sequence = Column(Text)
    componentTypeId = Column(
        ForeignKey(
            "ComponentType.componentTypeId", ondelete="CASCADE", onupdate="CASCADE"
        ),
        index=True,
    )
    concentrationTypeId = Column(
        ForeignKey(
            "ConcentrationType.concentrationTypeId",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        index=True,
    )
    externalId = Column(BINARY(16))
    density = Column(Float)
    abundance = Column(Float, comment="Deprecated")
    isotropy = Column(Enum("isotropic", "anisotropic"))

    ComponentType = relationship("ComponentType")
    ConcentrationType = relationship("ConcentrationType")
    Proposal = relationship("Proposal")


class SWOnceToken(Base):
    __tablename__ = "SW_onceToken"
    __table_args__ = {
        "comment": "One-time use tokens needed for token auth in order to grant access to file downloads and webcams (and some images)"
    }

    onceTokenId = Column(INTEGER(11), primary_key=True)
    token = Column(String(128))
    personId = Column(ForeignKey("Person.personId"), index=True)
    proposalId = Column(ForeignKey("Proposal.proposalId"), index=True)
    validity = Column(String(200))
    recordTimeStamp = Column(
        TIMESTAMP,
        nullable=False,
        index=True,
        server_default=text("current_timestamp()"),
    )

    Person = relationship("Person")
    Proposal = relationship("Proposal")


class Crystal(Base):
    __tablename__ = "Crystal"

    crystalId = Column(INTEGER(10), primary_key=True)
    proteinId = Column(
        ForeignKey("Protein.proteinId", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
        server_default=text("0"),
    )
    name = Column(String(255))
    spaceGroup = Column(String(20))
    morphology = Column(String(255))
    color = Column(String(45))
    size_X = Column(Float(asdecimal=True))
    size_Y = Column(Float(asdecimal=True))
    size_Z = Column(Float(asdecimal=True))
    cell_a = Column(Float(asdecimal=True))
    cell_b = Column(Float(asdecimal=True))
    cell_c = Column(Float(asdecimal=True))
    cell_alpha = Column(Float(asdecimal=True))
    cell_beta = Column(Float(asdecimal=True))
    cell_gamma = Column(Float(asdecimal=True))
    comments = Column(String(255))
    recordTimeStamp = Column(
        TIMESTAMP,
        nullable=False,
        server_default=text("current_timestamp()"),
        comment="Creation or last update date/time",
    )
    abundance = Column(Float)
    theoreticalDensity = Column(Float)

    Protein = relationship("Protein")


class SessionType(Base):
    __tablename__ = "SessionType"

    sessionTypeId = Column(INTEGER(10), primary_key=True)
    sessionId = Column(
        ForeignKey("BLSession.sessionId", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    typeName = Column(String(31), nullable=False)

    BLSession = relationship("BLSession")


class SessionHasPerson(Base):
    __tablename__ = "Session_has_Person"

    sessionId = Column(
        ForeignKey("BLSession.sessionId", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
        nullable=False,
        server_default=text("0"),
    )
    personId = Column(
        ForeignKey("Person.personId", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
        nullable=False,
        index=True,
        server_default=text("0"),
    )
    role = Column(
        Enum(
            "Local Contact",
            "Local Contact 2",
            "Staff",
            "Team Leader",
            "Co-Investigator",
            "Principal Investigator",
            "Alternate Contact",
            "Data Access",
            "Team Member",
            "ERA Admin",
            "Associate",
        )
    )
    remote = Column(TINYINT(1), server_default=text("0"))

    Person = relationship("Person")
    BLSession = relationship("BLSession")


class Shipping(Base):
    __tablename__ = "Shipping"

    shippingId = Column(INTEGER(10), primary_key=True)
    proposalId = Column(
        ForeignKey("Proposal.proposalId", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
        server_default=text("0"),
    )
    shippingName = Column(String(45), index=True)
    deliveryAgent_agentName = Column(String(45))
    deliveryAgent_shippingDate = Column(Date)
    deliveryAgent_deliveryDate = Column(Date)
    deliveryAgent_agentCode = Column(String(45))
    deliveryAgent_flightCode = Column(String(45))
    shippingStatus = Column(String(45), index=True)
    bltimeStamp = Column(DateTime)
    laboratoryId = Column(INTEGER(10), index=True)
    isStorageShipping = Column(TINYINT(1), server_default=text("0"))
    creationDate = Column(DateTime, index=True)
    comments = Column(String(1000))
    sendingLabContactId = Column(
        ForeignKey("LabContact.labContactId", ondelete="CASCADE", onupdate="CASCADE"),
        index=True,
    )
    returnLabContactId = Column(
        ForeignKey("LabContact.labContactId", ondelete="CASCADE", onupdate="CASCADE"),
        index=True,
    )
    returnCourier = Column(String(45))
    dateOfShippingToUser = Column(DateTime)
    shippingType = Column(String(45))
    SAFETYLEVEL = Column(String(8))
    deliveryAgent_flightCodeTimestamp = Column(
        TIMESTAMP, comment="Date flight code created, if automatic"
    )
    deliveryAgent_label = Column(Text, comment="Base64 encoded pdf of airway label")
    readyByTime = Column(Time, comment="Time shipment will be ready")
    closeTime = Column(Time, comment="Time after which shipment cannot be picked up")
    physicalLocation = Column(
        String(50), comment="Where shipment can be picked up from: i.e. Stores"
    )
    deliveryAgent_pickupConfirmationTimestamp = Column(
        TIMESTAMP, comment="Date picked confirmed"
    )
    deliveryAgent_pickupConfirmation = Column(
        String(10), comment="Confirmation number of requested pickup"
    )
    deliveryAgent_readyByTime = Column(Time, comment="Confirmed ready-by time")
    deliveryAgent_callinTime = Column(Time, comment="Confirmed courier call-in time")
    deliveryAgent_productcode = Column(
        String(10), comment="A code that identifies which shipment service was used"
    )
    deliveryAgent_flightCodePersonId = Column(
        ForeignKey("Person.personId"),
        index=True,
        comment="The person who created the AWB (for auditing)",
    )

    Person = relationship("Person")
    Proposal = relationship("Proposal")
    LabContact = relationship(
        "LabContact",
        primaryjoin="Shipping.returnLabContactId == LabContact.labContactId",
    )
    LabContact1 = relationship(
        "LabContact",
        primaryjoin="Shipping.sendingLabContactId == LabContact.labContactId",
    )


class Dewar(Base):
    __tablename__ = "Dewar"

    dewarId = Column(INTEGER(10), primary_key=True)
    shippingId = Column(
        ForeignKey("Shipping.shippingId", ondelete="CASCADE", onupdate="CASCADE"),
        index=True,
    )
    code = Column(String(45), index=True)
    comments = Column(TINYTEXT)
    storageLocation = Column(String(45))
    dewarStatus = Column(String(45), index=True)
    bltimeStamp = Column(DateTime)
    isStorageDewar = Column(TINYINT(1), server_default=text("0"))
    barCode = Column(String(45), unique=True)
    firstExperimentId = Column(
        ForeignKey("BLSession.sessionId", ondelete="SET NULL", onupdate="CASCADE"),
        index=True,
    )
    customsValue = Column(INTEGER(11))
    transportValue = Column(INTEGER(11))
    trackingNumberToSynchrotron = Column(String(30))
    trackingNumberFromSynchrotron = Column(String(30))
    type = Column(
        Enum("Dewar", "Toolbox", "Parcel"),
        nullable=False,
        server_default=text("'Dewar'"),
    )
    facilityCode = Column(String(20))
    weight = Column(Float, comment="dewar weight in kg")
    deliveryAgent_barcode = Column(
        String(30), comment="Courier piece barcode (not the airway bill)"
    )

    BLSession = relationship("BLSession")
    Shipping = relationship("Shipping")


class Container(Base):
    __tablename__ = "Container"

    containerId = Column(INTEGER(10), primary_key=True)
    dewarId = Column(
        ForeignKey("Dewar.dewarId", ondelete="CASCADE", onupdate="CASCADE"), index=True
    )
    code = Column(String(45))
    containerType = Column(String(20))
    capacity = Column(INTEGER(10))
    sampleChangerLocation = Column(String(20))
    containerStatus = Column(String(45), index=True)
    bltimeStamp = Column(DateTime)
    beamlineLocation = Column(String(20), index=True)
    screenId = Column(INTEGER(11), index=True)
    barcode = Column(String(45), unique=True)
    comments = Column(String(255))
    storageTemperature = Column(Float, comment="NULL=ambient")
    containerTypeId = Column(ForeignKey("ContainerType.containerTypeId"), index=True)
    currentDewarId = Column(
        ForeignKey("Dewar.dewarId"),
        index=True,
        comment="The dewar with which the container is currently associated",
    )

    ContainerType = relationship("ContainerType")
    Dewar = relationship(
        "Dewar", primaryjoin="Container.currentDewarId == Dewar.dewarId"
    )
    Dewar1 = relationship("Dewar", primaryjoin="Container.dewarId == Dewar.dewarId")


class BLSample(Base):
    __tablename__ = "BLSample"
    __table_args__ = (Index("crystalId", "crystalId", "containerId"),)

    blSampleId = Column(INTEGER(10), primary_key=True)
    crystalId = Column(
        ForeignKey("Crystal.crystalId", ondelete="CASCADE", onupdate="CASCADE")
    )
    containerId = Column(
        ForeignKey("Container.containerId", ondelete="CASCADE", onupdate="CASCADE"),
        index=True,
    )
    name = Column(String(100), index=True)
    code = Column(String(45))
    location = Column(String(45))
    comments = Column(String(1024))
    POSITIONID = Column(INTEGER(11))
    recordTimeStamp = Column(
        TIMESTAMP,
        nullable=False,
        server_default=text("current_timestamp()"),
        comment="Creation or last update date/time",
    )
    SMILES = Column(
        String(400),
        comment="the symbolic description of the structure of a chemical compound",
    )
    volume = Column(Float)
    staffComments = Column(String(255), comment="Any staff comments on the sample")
    extraMetadata = Column(LONGTEXT)

    Container = relationship("Container")
    Crystal = relationship("Crystal")


class ContainerHistory(Base):
    __tablename__ = "ContainerHistory"

    containerHistoryId = Column(INTEGER(11), primary_key=True)
    containerId = Column(
        ForeignKey("Container.containerId", ondelete="CASCADE", onupdate="CASCADE"),
        index=True,
    )
    location = Column(String(45))
    blTimeStamp = Column(
        TIMESTAMP, nullable=False, server_default=text("current_timestamp()")
    )
    status = Column(String(45))
    beamlineName = Column(String(20))
    currentDewarId = Column(
        ForeignKey("Dewar.dewarId"),
        index=True,
        comment="The dewar with which the container was associated at the creation of this row",
    )

    Container = relationship("Container")
    Dewar = relationship("Dewar")


class ContainerInspection(Base):
    __tablename__ = "ContainerInspection"
    __table_args__ = (
        Index("ContainerInspection_idx4", "containerId", "state", "manual"),
    )

    containerInspectionId = Column(INTEGER(11), primary_key=True)
    containerId = Column(
        ForeignKey("Container.containerId", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    inspectionTypeId = Column(
        ForeignKey("InspectionType.inspectionTypeId"), nullable=False, index=True
    )
    temperature = Column(Float)
    blTimeStamp = Column(DateTime)
    state = Column(String(20))
    priority = Column(SMALLINT(6))
    manual = Column(TINYINT(1))
    scheduledTimeStamp = Column(DateTime)
    completedTimeStamp = Column(DateTime)

    Container = relationship("Container")
    InspectionType = relationship("InspectionType")


class ContainerQueue(Base):
    __tablename__ = "ContainerQueue"

    containerQueueId = Column(INTEGER(11), primary_key=True)
    containerId = Column(
        ForeignKey("Container.containerId", ondelete="CASCADE", onupdate="CASCADE"),
        index=True,
    )
    personId = Column(ForeignKey("Person.personId", onupdate="CASCADE"), index=True)
    createdTimeStamp = Column(
        TIMESTAMP, nullable=False, server_default=text("current_timestamp()")
    )
    completedTimeStamp = Column(TIMESTAMP)

    Container = relationship("Container")
    Person = relationship("Person")


class BLSampleImage(Base):
    __tablename__ = "BLSampleImage"

    blSampleImageId = Column(INTEGER(11), primary_key=True)
    blSampleId = Column(ForeignKey("BLSample.blSampleId"), nullable=False, index=True)
    micronsPerPixelX = Column(Float)
    micronsPerPixelY = Column(Float)
    imageFullPath = Column(String(255), unique=True)
    comments = Column(String(255))
    blTimeStamp = Column(DateTime)
    containerInspectionId = Column(
        ForeignKey("ContainerInspection.containerInspectionId"), index=True
    )
    modifiedTimeStamp = Column(DateTime)
    offsetX = Column(
        INTEGER(11),
        nullable=False,
        server_default=text("0"),
        comment="The x offset of the image relative to the canvas",
    )
    offsetY = Column(
        INTEGER(11),
        nullable=False,
        server_default=text("0"),
        comment="The y offset of the image relative to the canvas",
    )

    BLSample = relationship("BLSample")
    ContainerInspection = relationship("ContainerInspection")


class BLSampleHasDataCollectionPlan(Base):
    __tablename__ = "BLSample_has_DataCollectionPlan"

    blSampleId = Column(
        ForeignKey("BLSample.blSampleId"), primary_key=True, nullable=False
    )
    dataCollectionPlanId = Column(
        ForeignKey("DiffractionPlan.diffractionPlanId"),
        primary_key=True,
        nullable=False,
        index=True,
    )
    planOrder = Column(TINYINT(3))

    BLSample = relationship("BLSample")
    DiffractionPlan = relationship("DiffractionPlan")


class BLSampleHasPositioner(Base):
    __tablename__ = "BLSample_has_Positioner"

    blSampleHasPositioner = Column(INTEGER(10), primary_key=True)
    blSampleId = Column(ForeignKey("BLSample.blSampleId"), nullable=False, index=True)
    positionerId = Column(
        ForeignKey("Positioner.positionerId"), nullable=False, index=True
    )

    BLSample = relationship("BLSample")
    Positioner = relationship("Positioner")


class DataCollectionGroup(Base):
    __tablename__ = "DataCollectionGroup"
    __table_args__ = {
        "comment": "a dataCollectionGroup is a group of dataCollection for a spe"
    }

    dataCollectionGroupId = Column(
        INTEGER(11), primary_key=True, comment="Primary key (auto-incremented)"
    )
    sessionId = Column(
        ForeignKey("BLSession.sessionId", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
        comment="references Session table",
    )
    comments = Column(String(1024), comment="comments")
    blSampleId = Column(
        ForeignKey("BLSample.blSampleId", ondelete="CASCADE", onupdate="CASCADE"),
        index=True,
        comment="references BLSample table",
    )
    experimentType = Column(
        Enum(
            "SAD",
            "SAD - Inverse Beam",
            "OSC",
            "Collect - Multiwedge",
            "MAD",
            "Helical",
            "Multi-positional",
            "Mesh",
            "Burn",
            "MAD - Inverse Beam",
            "Characterization",
            "Dehydration",
            "tomo",
            "experiment",
            "EM",
            "PDF",
            "PDF+Bragg",
            "Bragg",
            "single particle",
            "Serial Fixed",
            "Serial Jet",
            "Standard",
            "Time Resolved",
            "Diamond Anvil High Pressure",
            "Custom",
            "XRF map",
            "Energy scan",
            "XRF spectrum",
            "XRF map xas",
            "Mesh3D",
            "Screening",
            "XRD map",
            "XRF xrd map",
        ),
        comment="Standard: Routine structure determination experiment. Time Resolved: Investigate the change of a system over time. Custom: Special or non-standard data collection.",
    )
    startTime = Column(DateTime, comment="Start time of the dataCollectionGroup")
    endTime = Column(DateTime, comment="end time of the dataCollectionGroup")
    workflowId = Column(
        ForeignKey("Workflow.workflowId", ondelete="CASCADE", onupdate="CASCADE"),
        index=True,
    )
    xtalSnapshotFullPath = Column(String(255))
    scanParameters = Column(LONGTEXT)
    experimentTypeId = Column(ForeignKey("ExperimentType.experimentTypeId"), index=True)

    BLSample = relationship("BLSample")
    ExperimentType = relationship("ExperimentType")
    BLSession = relationship("BLSession")
    Workflow = relationship("Workflow")


class RobotAction(Base):
    __tablename__ = "RobotAction"
    __table_args__ = {"comment": "Robot actions as reported by GDA"}

    robotActionId = Column(INTEGER(11), primary_key=True)
    blsessionId = Column(ForeignKey("BLSession.sessionId"), nullable=False, index=True)
    blsampleId = Column(ForeignKey("BLSample.blSampleId"), index=True)
    actionType = Column(
        Enum(
            "LOAD",
            "UNLOAD",
            "DISPOSE",
            "STORE",
            "WASH",
            "ANNEAL",
            "MOSAIC",
            "REFERENCE",
        )
    )
    startTimestamp = Column(
        TIMESTAMP,
        nullable=False,
        server_default=text("current_timestamp() ON UPDATE current_timestamp()"),
    )
    endTimestamp = Column(
        TIMESTAMP, nullable=False, server_default=text("'0000-00-00 00:00:00'")
    )
    status = Column(
        Enum("SUCCESS", "ERROR", "CRITICAL", "WARNING", "EPICSFAIL", "COMMANDNOTSENT")
    )
    message = Column(String(255))
    containerLocation = Column(SMALLINT(6))
    dewarLocation = Column(SMALLINT(6))
    sampleBarcode = Column(String(45))
    xtalSnapshotBefore = Column(String(255))
    xtalSnapshotAfter = Column(String(255))
    resultFilePath = Column(String(255))

    BLSample = relationship("BLSample")
    BLSession = relationship("BLSession")


class XRFFluorescenceMappingROI(Base):
    __tablename__ = "XRFFluorescenceMappingROI"

    xrfFluorescenceMappingROIId = Column(INTEGER(11), primary_key=True)
    startEnergy = Column(Float, nullable=False)
    endEnergy = Column(Float, nullable=False)
    element = Column(String(2))
    edge = Column(
        String(15),
        comment="Edge type i.e. Ka1, could be a custom edge in case of overlap Ka1-noCa",
    )
    r = Column(TINYINT(3), comment="R colour component")
    g = Column(TINYINT(3), comment="G colour component")
    b = Column(TINYINT(3), comment="B colour component")
    blSampleId = Column(
        ForeignKey("BLSample.blSampleId"),
        index=True,
        comment="ROIs can be created within the context of a sample",
    )
    scalar = Column(
        String(50),
        comment="For ROIs that are not an element, i.e. could be a scan counter instead",
    )

    BLSample = relationship("BLSample")


class BLSampleImageHasPositioner(Base):
    __tablename__ = "BLSampleImage_has_Positioner"
    __table_args__ = {
        "comment": "Allows a BLSampleImage to store motor positions along with the image"
    }

    blSampleImageHasPositionerId = Column(INTEGER(10), primary_key=True)
    blSampleImageId = Column(
        ForeignKey("BLSampleImage.blSampleImageId"), nullable=False, index=True
    )
    positionerId = Column(
        ForeignKey("Positioner.positionerId"), nullable=False, index=True
    )
    value = Column(
        Float, comment="The position of this positioner for this blsampleimage"
    )

    BLSampleImage = relationship("BLSampleImage")
    Positioner = relationship("Positioner")


class BLSubSample(Base):
    __tablename__ = "BLSubSample"

    blSubSampleId = Column(
        INTEGER(11), primary_key=True, comment="Primary key (auto-incremented)"
    )
    blSampleId = Column(
        ForeignKey("BLSample.blSampleId", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
        comment="sample",
    )
    blSampleImageId = Column(ForeignKey("BLSampleImage.blSampleImageId"), index=True)
    positionId = Column(
        ForeignKey("Position.positionId", ondelete="CASCADE", onupdate="CASCADE"),
        index=True,
        comment="position of the subsample",
    )
    position2Id = Column(
        ForeignKey("Position.positionId", ondelete="CASCADE", onupdate="CASCADE"),
        index=True,
    )
    comments = Column(String(1024), comment="comments")
    recordTimeStamp = Column(
        TIMESTAMP,
        nullable=False,
        server_default=text("current_timestamp()"),
        comment="Creation or last update date/time",
    )
    source = Column(
        Enum("manual", "auto", "reference"), server_default=text("'manual'")
    )
    type = Column(
        String(10),
        comment="The type of subsample, i.e. roi (region), poi (point), loi (line)",
    )
    extraMetadata = Column(LONGTEXT)

    BLSample = relationship("BLSample")
    BLSampleImage = relationship("BLSampleImage")
    Position = relationship(
        "Position", primaryjoin="BLSubSample.position2Id == Position.positionId"
    )
    Position1 = relationship(
        "Position", primaryjoin="BLSubSample.positionId == Position.positionId"
    )


class RobotActionPosition(Base):
    __tablename__ = "RobotActionPosition"
    __table_args__ = {
        "comment": "Store a series of x,y(,z) positions along with a Robot(Sample)Action"
    }

    robotActionPositionId = Column(INTEGER(11), primary_key=True)
    robotActionId = Column(
        ForeignKey("RobotAction.robotActionId", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    type = Column(Enum("reference", "real"))
    id = Column(TINYINT(3))
    posX = Column(Float(asdecimal=True))
    posY = Column(Float(asdecimal=True))
    posZ = Column(Float(asdecimal=True))

    RobotAction = relationship("RobotAction")


class BLSubSampleHasPositioner(Base):
    __tablename__ = "BLSubSample_has_Positioner"

    blSubSampleHasPositioner = Column(INTEGER(10), primary_key=True)
    blSubSampleId = Column(
        ForeignKey("BLSubSample.blSubSampleId"), nullable=False, index=True
    )
    positionerId = Column(
        ForeignKey("Positioner.positionerId"), nullable=False, index=True
    )

    BLSubSample = relationship("BLSubSample")
    Positioner = relationship("Positioner")


class ContainerQueueSample(Base):
    __tablename__ = "ContainerQueueSample"

    containerQueueSampleId = Column(INTEGER(11), primary_key=True)
    containerQueueId = Column(
        ForeignKey(
            "ContainerQueue.containerQueueId", ondelete="CASCADE", onupdate="CASCADE"
        ),
        index=True,
    )
    blSubSampleId = Column(
        ForeignKey("BLSubSample.blSubSampleId", ondelete="CASCADE", onupdate="CASCADE"),
        index=True,
    )
    status = Column(
        String(20),
        comment="The status of the queued item, i.e. skipped, reinspect. Completed / failed should be inferred from related DataCollection",
    )
    startTime = Column(DateTime, comment="Start time of processing the queue item")
    endTime = Column(DateTime, comment="End time of processing the queue item")
    dataCollectionPlanId = Column(
        ForeignKey("DiffractionPlan.diffractionPlanId"), index=True
    )
    blSampleId = Column(ForeignKey("BLSample.blSampleId"), index=True)

    BLSample = relationship("BLSample")
    BLSubSample = relationship("BLSubSample")
    ContainerQueue = relationship("ContainerQueue")
    DiffractionPlan = relationship("DiffractionPlan")


class DataCollection(Base):
    __tablename__ = "DataCollection"
    __table_args__ = (
        Index(
            "DataCollection_dataCollectionGroupId_startTime",
            "dataCollectionGroupId",
            "startTime",
        ),
    )

    dataCollectionId = Column(
        INTEGER(11), primary_key=True, comment="Primary key (auto-incremented)"
    )
    BLSAMPLEID = Column(INTEGER(11), index=True)
    SESSIONID = Column(INTEGER(11), index=True, server_default=text("0"))
    experimenttype = Column(String(24))
    dataCollectionNumber = Column(INTEGER(10), index=True)
    startTime = Column(DateTime, index=True, comment="Start time of the dataCollection")
    endTime = Column(DateTime, comment="end time of the dataCollection")
    runStatus = Column(String(45))
    axisStart = Column(Float)
    axisEnd = Column(Float)
    axisRange = Column(Float)
    numberOfImages = Column(INTEGER(10))
    numberOfPasses = Column(INTEGER(10))
    exposureTime = Column(Float)
    imageDirectory = Column(
        String(255),
        index=True,
        comment="The directory where files reside - should end with a slash",
    )
    imagePrefix = Column(String(45), index=True)
    imageSuffix = Column(String(45))
    imageContainerSubPath = Column(
        String(255),
        comment="Internal path of a HDF5 file pointing to the data for this data collection",
    )
    fileTemplate = Column(String(255))
    wavelength = Column(Float)
    resolution = Column(Float)
    detectorDistance = Column(Float)
    xBeam = Column(Float)
    yBeam = Column(Float)
    comments = Column(String(1024))
    transmission = Column(Float)
    xtalSnapshotFullPath1 = Column(String(255))
    xtalSnapshotFullPath2 = Column(String(255))
    xtalSnapshotFullPath3 = Column(String(255))
    xtalSnapshotFullPath4 = Column(String(255))
    rotationAxis = Column(Enum("Omega", "Kappa", "Phi"))
    beamSizeAtSampleX = Column(Float)
    beamSizeAtSampleY = Column(Float)
    dataCollectionGroupId = Column(
        ForeignKey("DataCollectionGroup.dataCollectionGroupId"),
        nullable=False,
        index=True,
        comment="references DataCollectionGroup table",
    )
    detectorId = Column(
        ForeignKey("Detector.detectorId"),
        index=True,
        comment="references Detector table",
    )
    flux = Column(Float(asdecimal=True))
    blSubSampleId = Column(ForeignKey("BLSubSample.blSubSampleId"), index=True)
    dataCollectionPlanId = Column(
        ForeignKey("DiffractionPlan.diffractionPlanId"), index=True
    )

    BLSubSample = relationship("BLSubSample")
    DataCollectionGroup = relationship("DataCollectionGroup")
    DiffractionPlan = relationship("DiffractionPlan")
    Detector = relationship("Detector")


class EnergyScan(Base):
    __tablename__ = "EnergyScan"

    energyScanId = Column(INTEGER(10), primary_key=True)
    sessionId = Column(
        ForeignKey("BLSession.sessionId", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    blSampleId = Column(ForeignKey("BLSample.blSampleId"), index=True)
    fluorescenceDetector = Column(String(255))
    scanFileFullPath = Column(String(255))
    jpegChoochFileFullPath = Column(String(255))
    element = Column(String(45))
    startEnergy = Column(Float)
    endEnergy = Column(Float)
    transmissionFactor = Column(Float)
    exposureTime = Column(Float)
    axisPosition = Column(Float)
    synchrotronCurrent = Column(Float)
    temperature = Column(Float)
    peakEnergy = Column(Float)
    peakFPrime = Column(Float)
    peakFDoublePrime = Column(Float)
    inflectionEnergy = Column(Float)
    inflectionFPrime = Column(Float)
    inflectionFDoublePrime = Column(Float)
    xrayDose = Column(Float)
    startTime = Column(DateTime)
    endTime = Column(DateTime)
    edgeEnergy = Column(String(255))
    filename = Column(String(255))
    beamSizeVertical = Column(Float)
    beamSizeHorizontal = Column(Float)
    choochFileFullPath = Column(String(255))
    crystalClass = Column(String(20))
    comments = Column(String(1024))
    flux = Column(Float(asdecimal=True), comment="flux measured before the energyScan")
    flux_end = Column(
        Float(asdecimal=True), comment="flux measured after the energyScan"
    )
    workingDirectory = Column(String(45))
    blSubSampleId = Column(ForeignKey("BLSubSample.blSubSampleId"), index=True)

    BLSample = relationship("BLSample")
    BLSubSample = relationship("BLSubSample")
    BLSession = relationship("BLSession")


class XFEFluorescenceSpectrum(Base):
    __tablename__ = "XFEFluorescenceSpectrum"

    xfeFluorescenceSpectrumId = Column(INTEGER(10), primary_key=True)
    sessionId = Column(
        ForeignKey("BLSession.sessionId", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    blSampleId = Column(
        ForeignKey("BLSample.blSampleId", ondelete="CASCADE", onupdate="CASCADE"),
        index=True,
    )
    jpegScanFileFullPath = Column(String(255))
    startTime = Column(DateTime)
    endTime = Column(DateTime)
    filename = Column(String(255))
    exposureTime = Column(Float)
    axisPosition = Column(Float)
    beamTransmission = Column(Float)
    annotatedPymcaXfeSpectrum = Column(String(255))
    fittedDataFileFullPath = Column(String(255))
    scanFileFullPath = Column(String(255))
    energy = Column(Float)
    beamSizeVertical = Column(Float)
    beamSizeHorizontal = Column(Float)
    crystalClass = Column(String(20))
    comments = Column(String(1024))
    blSubSampleId = Column(ForeignKey("BLSubSample.blSubSampleId"), index=True)
    flux = Column(Float(asdecimal=True), comment="flux measured before the xrfSpectra")
    flux_end = Column(
        Float(asdecimal=True), comment="flux measured after the xrfSpectra"
    )
    workingDirectory = Column(String(512))

    BLSample = relationship("BLSample")
    BLSubSample = relationship("BLSubSample")
    BLSession = relationship("BLSession")


class DataCollectionComment(Base):
    __tablename__ = "DataCollectionComment"

    dataCollectionCommentId = Column(INTEGER(11), primary_key=True)
    dataCollectionId = Column(
        ForeignKey(
            "DataCollection.dataCollectionId", ondelete="CASCADE", onupdate="CASCADE"
        ),
        nullable=False,
        index=True,
    )
    personId = Column(
        ForeignKey("Person.personId", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    comments = Column(String(4000))
    createTime = Column(
        DateTime, nullable=False, server_default=text("current_timestamp()")
    )
    modTime = Column(Date)

    DataCollection = relationship("DataCollection")
    Person = relationship("Person")


class DataCollectionFileAttachment(Base):
    __tablename__ = "DataCollectionFileAttachment"

    dataCollectionFileAttachmentId = Column(INTEGER(11), primary_key=True)
    dataCollectionId = Column(
        ForeignKey(
            "DataCollection.dataCollectionId", ondelete="CASCADE", onupdate="CASCADE"
        ),
        nullable=False,
        index=True,
    )
    fileFullPath = Column(String(255), nullable=False)
    fileType = Column(
        Enum("snapshot", "log", "xy", "recip", "pia", "warning", "params")
    )
    createTime = Column(
        TIMESTAMP, nullable=False, server_default=text("current_timestamp()")
    )

    DataCollection = relationship("DataCollection")


class GridInfo(Base):
    __tablename__ = "GridInfo"

    gridInfoId = Column(
        INTEGER(11), primary_key=True, comment="Primary key (auto-incremented)"
    )
    xOffset = Column(Float(asdecimal=True))
    yOffset = Column(Float(asdecimal=True))
    dx_mm = Column(Float(asdecimal=True))
    dy_mm = Column(Float(asdecimal=True))
    steps_x = Column(Float(asdecimal=True))
    steps_y = Column(Float(asdecimal=True))
    meshAngle = Column(Float(asdecimal=True))
    recordTimeStamp = Column(
        TIMESTAMP,
        nullable=False,
        server_default=text("current_timestamp()"),
        comment="Creation or last update date/time",
    )
    orientation = Column(
        Enum("vertical", "horizontal"), server_default=text("'horizontal'")
    )
    dataCollectionGroupId = Column(
        ForeignKey("DataCollectionGroup.dataCollectionGroupId"), index=True
    )
    pixelsPerMicronX = Column(Float)
    pixelsPerMicronY = Column(Float)
    snapshot_offsetXPixel = Column(Float)
    snapshot_offsetYPixel = Column(Float)
    snaked = Column(
        TINYINT(1),
        server_default=text("0"),
        comment="True: The images associated with the DCG were collected in a snaked pattern",
    )
    dataCollectionId = Column(
        ForeignKey(
            "DataCollection.dataCollectionId", ondelete="CASCADE", onupdate="CASCADE"
        ),
        index=True,
    )
    patchesX = Column(
        INTEGER(10),
        server_default=text("1"),
        comment="Number of patches the grid is made up of in the X direction",
    )
    patchesY = Column(
        INTEGER(10),
        server_default=text("1"),
        comment="Number of patches the grid is made up of in the Y direction",
    )

    DataCollectionGroup = relationship("DataCollectionGroup")
    DataCollection = relationship("DataCollection")


class Movie(Base):
    __tablename__ = "Movie"

    movieId = Column(INTEGER(11), primary_key=True)
    dataCollectionId = Column(ForeignKey("DataCollection.dataCollectionId"), index=True)
    movieNumber = Column(MEDIUMINT(8))
    movieFullPath = Column(String(255))
    createdTimeStamp = Column(
        TIMESTAMP,
        nullable=False,
        server_default=text("current_timestamp() ON UPDATE current_timestamp()"),
    )
    positionX = Column(Float)
    positionY = Column(Float)
    nominalDefocus = Column(Float, comment="Nominal defocus, Units: A")
    angle = Column(Float, comment="unit: degrees relative to perpendicular to beam")
    fluence = Column(
        Float,
        comment="accumulated electron fluence from start to end of acquisition of this movie (commonly, but incorrectly, referred to as ‘dose’)",
    )
    numberOfFrames = Column(
        INTEGER(11),
        comment="number of frames per movie. This should be equivalent to the number of\xa0MotionCorrectionDrift\xa0entries, but the latter is a property of data analysis, whereas the number of frames is an intrinsic property of acquisition.",
    )

    DataCollection = relationship("DataCollection")


class ProcessingJob(Base):
    __tablename__ = "ProcessingJob"
    __table_args__ = {"comment": "From this we get both job times and lag times"}

    processingJobId = Column(INTEGER(11), primary_key=True)
    dataCollectionId = Column(ForeignKey("DataCollection.dataCollectionId"), index=True)
    displayName = Column(String(80), comment="xia2, fast_dp, dimple, etc")
    comments = Column(
        String(255),
        comment="For users to annotate the job and see the motivation for the job",
    )
    recordTimestamp = Column(
        TIMESTAMP,
        nullable=False,
        server_default=text("current_timestamp()"),
        comment="When job was submitted",
    )
    recipe = Column(String(50), comment="What we want to run (xia, dimple, etc).")
    automatic = Column(
        TINYINT(1),
        comment="Whether this processing job was triggered automatically or not",
    )

    DataCollection = relationship("DataCollection")


class AutoProcProgram(Base):
    __tablename__ = "AutoProcProgram"

    autoProcProgramId = Column(
        INTEGER(10), primary_key=True, comment="Primary key (auto-incremented)"
    )
    processingCommandLine = Column(
        String(255), comment="Command line for running the automatic processing"
    )
    processingPrograms = Column(
        String(255), comment="Processing programs (comma separated)"
    )
    processingStatus = Column(TINYINT(1), comment="success (1) / fail (0)")
    processingMessage = Column(String(255), comment="warning, error,...")
    processingStartTime = Column(DateTime, comment="Processing start time")
    processingEndTime = Column(DateTime, comment="Processing end time")
    processingEnvironment = Column(String(255), comment="Cpus, Nodes,...")
    recordTimeStamp = Column(DateTime, comment="Creation or last update date/time")
    processingJobId = Column(ForeignKey("ProcessingJob.processingJobId"), index=True)

    ProcessingJob = relationship("ProcessingJob")


class ProcessingJobImageSweep(Base):
    __tablename__ = "ProcessingJobImageSweep"
    __table_args__ = {
        "comment": "This allows multiple sweeps per processing job for multi-xia2"
    }

    processingJobImageSweepId = Column(INTEGER(11), primary_key=True)
    processingJobId = Column(ForeignKey("ProcessingJob.processingJobId"), index=True)
    dataCollectionId = Column(ForeignKey("DataCollection.dataCollectionId"), index=True)
    startImage = Column(MEDIUMINT(8))
    endImage = Column(MEDIUMINT(8))

    DataCollection = relationship("DataCollection")
    ProcessingJob = relationship("ProcessingJob")


class ProcessingJobParameter(Base):
    __tablename__ = "ProcessingJobParameter"

    processingJobParameterId = Column(INTEGER(11), primary_key=True)
    processingJobId = Column(ForeignKey("ProcessingJob.processingJobId"), index=True)
    parameterKey = Column(String(80), comment="E.g. resolution, spacegroup, pipeline")
    parameterValue = Column(String(1024))

    ProcessingJob = relationship("ProcessingJob")


class AutoProcIntegration(Base):
    __tablename__ = "AutoProcIntegration"

    autoProcIntegrationId = Column(
        INTEGER(10), primary_key=True, comment="Primary key (auto-incremented)"
    )
    dataCollectionId = Column(
        ForeignKey(
            "DataCollection.dataCollectionId", ondelete="CASCADE", onupdate="CASCADE"
        ),
        nullable=False,
        index=True,
        comment="DataCollection item",
    )
    autoProcProgramId = Column(
        ForeignKey(
            "AutoProcProgram.autoProcProgramId", ondelete="CASCADE", onupdate="CASCADE"
        ),
        index=True,
        comment="Related program item",
    )
    startImageNumber = Column(INTEGER(10), comment="start image number")
    endImageNumber = Column(INTEGER(10), comment="end image number")
    refinedDetectorDistance = Column(
        Float, comment="Refined DataCollection.detectorDistance"
    )
    refinedXBeam = Column(Float, comment="Refined DataCollection.xBeam")
    refinedYBeam = Column(Float, comment="Refined DataCollection.yBeam")
    rotationAxisX = Column(Float, comment="Rotation axis")
    rotationAxisY = Column(Float, comment="Rotation axis")
    rotationAxisZ = Column(Float, comment="Rotation axis")
    beamVectorX = Column(Float, comment="Beam vector")
    beamVectorY = Column(Float, comment="Beam vector")
    beamVectorZ = Column(Float, comment="Beam vector")
    cell_a = Column(Float, comment="Unit cell")
    cell_b = Column(Float, comment="Unit cell")
    cell_c = Column(Float, comment="Unit cell")
    cell_alpha = Column(Float, comment="Unit cell")
    cell_beta = Column(Float, comment="Unit cell")
    cell_gamma = Column(Float, comment="Unit cell")
    recordTimeStamp = Column(DateTime, comment="Creation or last update date/time")
    anomalous = Column(
        TINYINT(1), server_default=text("0"), comment="boolean type:0 noanoum - 1 anoum"
    )

    AutoProcProgram = relationship("AutoProcProgram")
    DataCollection = relationship("DataCollection")


class AutoProcProgramAttachment(Base):
    __tablename__ = "AutoProcProgramAttachment"

    autoProcProgramAttachmentId = Column(
        INTEGER(10), primary_key=True, comment="Primary key (auto-incremented)"
    )
    autoProcProgramId = Column(
        ForeignKey(
            "AutoProcProgram.autoProcProgramId", ondelete="CASCADE", onupdate="CASCADE"
        ),
        nullable=False,
        index=True,
        comment="Related autoProcProgram item",
    )
    fileType = Column(
        Enum("Log", "Result", "Graph", "Debug", "Input"),
        comment="Type of file Attachment",
    )
    fileName = Column(String(255), comment="Attachment filename")
    filePath = Column(String(255), comment="Attachment filepath to disk storage")
    recordTimeStamp = Column(DateTime, comment="Creation or last update date/time")
    importanceRank = Column(
        TINYINT(3),
        comment="For the particular autoProcProgramId and fileType, indicate the importance of the attachment. Higher numbers are more important",
    )

    AutoProcProgram = relationship("AutoProcProgram")


class AutoProcProgramMessage(Base):
    __tablename__ = "AutoProcProgramMessage"

    autoProcProgramMessageId = Column(INTEGER(10), primary_key=True)
    autoProcProgramId = Column(
        ForeignKey("AutoProcProgram.autoProcProgramId"), index=True
    )
    recordTimeStamp = Column(
        TIMESTAMP, nullable=False, server_default=text("current_timestamp()")
    )
    severity = Column(Enum("ERROR", "WARNING", "INFO"))
    message = Column(String(200))
    description = Column(Text)

    AutoProcProgram = relationship("AutoProcProgram")


class MotionCorrection(Base):
    __tablename__ = "MotionCorrection"

    motionCorrectionId = Column(INTEGER(11), primary_key=True)
    dataCollectionId = Column(ForeignKey("DataCollection.dataCollectionId"), index=True)
    autoProcProgramId = Column(
        ForeignKey("AutoProcProgram.autoProcProgramId"), index=True
    )
    imageNumber = Column(SMALLINT(5), comment="Movie number, sequential in time 1-n")
    firstFrame = Column(SMALLINT(5), comment="First frame of movie used")
    lastFrame = Column(SMALLINT(5), comment="Last frame of movie used")
    dosePerFrame = Column(Float, comment="Dose per frame, Units: e-/A^2")
    doseWeight = Column(Float, comment="Dose weight, Units: dimensionless")
    totalMotion = Column(Float, comment="Total motion, Units: A")
    averageMotionPerFrame = Column(Float, comment="Average motion per frame, Units: A")
    driftPlotFullPath = Column(String(255), comment="Full path to the drift plot")
    micrographFullPath = Column(String(255), comment="Full path to the micrograph")
    micrographSnapshotFullPath = Column(
        String(255), comment="Full path to a snapshot (jpg) of the micrograph"
    )
    patchesUsedX = Column(
        MEDIUMINT(8), comment="Number of patches used in x (for motioncor2)"
    )
    patchesUsedY = Column(
        MEDIUMINT(8), comment="Number of patches used in y (for motioncor2)"
    )
    fftFullPath = Column(
        String(255), comment="Full path to the jpg image of the raw micrograph FFT"
    )
    fftCorrectedFullPath = Column(
        String(255),
        comment="Full path to the jpg image of the drift corrected micrograph FFT",
    )
    comments = Column(String(255))
    movieId = Column(ForeignKey("Movie.movieId"), index=True)

    AutoProcProgram = relationship("AutoProcProgram")
    DataCollection = relationship("DataCollection")
    Movie = relationship("Movie")


class Screening(Base):
    __tablename__ = "Screening"

    screeningId = Column(INTEGER(10), primary_key=True)
    dataCollectionId = Column(
        ForeignKey(
            "DataCollection.dataCollectionId", ondelete="CASCADE", onupdate="CASCADE"
        ),
        index=True,
    )
    bltimeStamp = Column(
        TIMESTAMP,
        nullable=False,
        server_default=text("current_timestamp() ON UPDATE current_timestamp()"),
    )
    programVersion = Column(String(45))
    comments = Column(String(255))
    shortComments = Column(String(20))
    diffractionPlanId = Column(
        INTEGER(10), index=True, comment="references DiffractionPlan"
    )
    dataCollectionGroupId = Column(
        ForeignKey("DataCollectionGroup.dataCollectionGroupId"), index=True
    )
    xmlSampleInformation = Column(LONGBLOB)
    autoProcProgramId = Column(
        ForeignKey(
            "AutoProcProgram.autoProcProgramId", ondelete="SET NULL", onupdate="CASCADE"
        ),
        index=True,
    )

    AutoProcProgram = relationship("AutoProcProgram")
    DataCollectionGroup = relationship("DataCollectionGroup")
    DataCollection = relationship("DataCollection")


class XRFFluorescenceMapping(Base):
    __tablename__ = "XRFFluorescenceMapping"
    __table_args__ = {
        "comment": "An XRF map generated from an XRF Mapping ROI based on data from a gridscan of a sample"
    }

    xrfFluorescenceMappingId = Column(INTEGER(11), primary_key=True)
    xrfFluorescenceMappingROIId = Column(
        ForeignKey(
            "XRFFluorescenceMappingROI.xrfFluorescenceMappingROIId",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        nullable=False,
        index=True,
    )
    gridInfoId = Column(ForeignKey("GridInfo.gridInfoId"), nullable=False, index=True)
    dataFormat = Column(
        String(15),
        nullable=False,
        comment="Description of format and any compression, i.e. json+gzip for gzipped json",
    )
    data = Column(LONGBLOB, nullable=False, comment="The actual data")
    points = Column(
        INTEGER(11), comment="The number of points available, for realtime feedback"
    )
    opacity = Column(
        Float, nullable=False, server_default=text("1"), comment="Display opacity"
    )
    colourMap = Column(String(20), comment="Colour map for displaying the data")
    min = Column(Float, comment="Min value in the data for histogramming")
    max = Column(Float, comment="Max value in the data for histogramming")
    autoProcProgramId = Column(
        ForeignKey("AutoProcProgram.autoProcProgramId"),
        index=True,
        comment="Related autoproc programid",
    )
    scale = Column(
        String(25), comment="Define the scale type for this map, linear, logarithmic"
    )

    AutoProcProgram = relationship("AutoProcProgram")
    GridInfo = relationship("GridInfo")
    XRFFluorescenceMappingROI = relationship("XRFFluorescenceMappingROI")


class AutoProcScalingHasInt(Base):
    __tablename__ = "AutoProcScaling_has_Int"
    __table_args__ = (
        Index(
            "AutoProcScalingHasInt_FKIndex3",
            "autoProcScalingId",
            "autoProcIntegrationId",
        ),
    )

    autoProcScaling_has_IntId = Column(
        INTEGER(10), primary_key=True, comment="Primary key (auto-incremented)"
    )
    autoProcScalingId = Column(
        ForeignKey(
            "AutoProcScaling.autoProcScalingId", ondelete="CASCADE", onupdate="CASCADE"
        ),
        comment="AutoProcScaling item",
    )
    autoProcIntegrationId = Column(
        ForeignKey(
            "AutoProcIntegration.autoProcIntegrationId",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        nullable=False,
        index=True,
        comment="AutoProcIntegration item",
    )
    recordTimeStamp = Column(DateTime, comment="Creation or last update date/time")

    AutoProcIntegration = relationship("AutoProcIntegration")
    AutoProcScaling = relationship("AutoProcScaling")


class AutoProcStatus(Base):
    __tablename__ = "AutoProcStatus"
    __table_args__ = {
        "comment": "AutoProcStatus table is linked to AutoProcIntegration"
    }

    autoProcStatusId = Column(
        INTEGER(11), primary_key=True, comment="Primary key (auto-incremented)"
    )
    autoProcIntegrationId = Column(
        ForeignKey(
            "AutoProcIntegration.autoProcIntegrationId",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        nullable=False,
        index=True,
    )
    step = Column(
        Enum("Indexing", "Integration", "Correction", "Scaling", "Importing"),
        nullable=False,
        comment="autoprocessing step",
    )
    status = Column(
        Enum("Launched", "Successful", "Failed"),
        nullable=False,
        comment="autoprocessing status",
    )
    comments = Column(String(1024), comment="comments")
    bltimeStamp = Column(
        TIMESTAMP,
        nullable=False,
        server_default=text("current_timestamp() ON UPDATE current_timestamp()"),
    )

    AutoProcIntegration = relationship("AutoProcIntegration")


class CTF(Base):
    __tablename__ = "CTF"

    ctfId = Column(INTEGER(11), primary_key=True)
    motionCorrectionId = Column(
        ForeignKey("MotionCorrection.motionCorrectionId"), index=True
    )
    autoProcProgramId = Column(
        ForeignKey("AutoProcProgram.autoProcProgramId"), index=True
    )
    boxSizeX = Column(Float, comment="Box size in x, Units: pixels")
    boxSizeY = Column(Float, comment="Box size in y, Units: pixels")
    minResolution = Column(Float, comment="Minimum resolution for CTF, Units: A")
    maxResolution = Column(Float, comment="Units: A")
    minDefocus = Column(Float, comment="Units: A")
    maxDefocus = Column(Float, comment="Units: A")
    defocusStepSize = Column(Float, comment="Units: A")
    astigmatism = Column(Float, comment="Units: A")
    astigmatismAngle = Column(Float, comment="Units: deg?")
    estimatedResolution = Column(Float, comment="Units: A")
    estimatedDefocus = Column(Float, comment="Units: A")
    amplitudeContrast = Column(Float, comment="Units: %?")
    ccValue = Column(Float, comment="Correlation value")
    fftTheoreticalFullPath = Column(
        String(255), comment="Full path to the jpg image of the simulated FFT"
    )
    comments = Column(String(255))

    AutoProcProgram = relationship("AutoProcProgram")
    MotionCorrection = relationship("MotionCorrection")


class ScreeningInput(Base):
    __tablename__ = "ScreeningInput"

    screeningInputId = Column(INTEGER(10), primary_key=True)
    screeningId = Column(
        ForeignKey("Screening.screeningId", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
        server_default=text("0"),
    )
    beamX = Column(Float)
    beamY = Column(Float)
    rmsErrorLimits = Column(Float)
    minimumFractionIndexed = Column(Float)
    maximumFractionRejected = Column(Float)
    minimumSignalToNoise = Column(Float)
    diffractionPlanId = Column(INTEGER(10), comment="references DiffractionPlan table")
    xmlSampleInformation = Column(LONGBLOB)

    Screening = relationship("Screening")


class ScreeningOutput(Base):
    __tablename__ = "ScreeningOutput"

    screeningOutputId = Column(INTEGER(10), primary_key=True)
    screeningId = Column(
        ForeignKey("Screening.screeningId", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
        server_default=text("0"),
    )
    statusDescription = Column(String(1024))
    rejectedReflections = Column(INTEGER(10))
    resolutionObtained = Column(Float)
    spotDeviationR = Column(Float)
    spotDeviationTheta = Column(Float)
    beamShiftX = Column(Float)
    beamShiftY = Column(Float)
    numSpotsFound = Column(INTEGER(10))
    numSpotsUsed = Column(INTEGER(10))
    numSpotsRejected = Column(INTEGER(10))
    mosaicity = Column(Float)
    iOverSigma = Column(Float)
    diffractionRings = Column(TINYINT(1))
    SCREENINGSUCCESS = Column(
        TINYINT(1), server_default=text("0"), comment="Column to be deleted"
    )
    mosaicityEstimated = Column(TINYINT(1), nullable=False, server_default=text("0"))
    rankingResolution = Column(Float(asdecimal=True))
    program = Column(String(45))
    doseTotal = Column(Float(asdecimal=True))
    totalExposureTime = Column(Float(asdecimal=True))
    totalRotationRange = Column(Float(asdecimal=True))
    totalNumberOfImages = Column(INTEGER(11))
    rFriedel = Column(Float(asdecimal=True))
    indexingSuccess = Column(TINYINT(1), nullable=False, server_default=text("0"))
    strategySuccess = Column(TINYINT(1), nullable=False, server_default=text("0"))
    alignmentSuccess = Column(TINYINT(1), nullable=False, server_default=text("0"))

    Screening = relationship("Screening")


class XFEFluorescenceComposite(Base):
    __tablename__ = "XFEFluorescenceComposite"
    __table_args__ = {
        "comment": "A composite XRF map composed of three XRFFluorescenceMapping entries creating r, g, b layers"
    }

    xfeFluorescenceCompositeId = Column(INTEGER(10), primary_key=True)
    r = Column(
        ForeignKey("XRFFluorescenceMapping.xrfFluorescenceMappingId"),
        nullable=False,
        index=True,
        comment="Red layer",
    )
    g = Column(
        ForeignKey("XRFFluorescenceMapping.xrfFluorescenceMappingId"),
        nullable=False,
        index=True,
        comment="Green layer",
    )
    b = Column(
        ForeignKey("XRFFluorescenceMapping.xrfFluorescenceMappingId"),
        nullable=False,
        index=True,
        comment="Blue layer",
    )
    rOpacity = Column(
        Float, nullable=False, server_default=text("1"), comment="Red layer opacity"
    )
    bOpacity = Column(
        Float, nullable=False, server_default=text("1"), comment="Red layer opacity"
    )
    gOpacity = Column(
        Float, nullable=False, server_default=text("1"), comment="Red layer opacity"
    )
    opacity = Column(
        Float, nullable=False, server_default=text("1"), comment="Total map opacity"
    )

    XRFFluorescenceMapping = relationship(
        "XRFFluorescenceMapping",
        primaryjoin="XFEFluorescenceComposite.b == XRFFluorescenceMapping.xrfFluorescenceMappingId",
    )
    XRFFluorescenceMapping1 = relationship(
        "XRFFluorescenceMapping",
        primaryjoin="XFEFluorescenceComposite.g == XRFFluorescenceMapping.xrfFluorescenceMappingId",
    )
    XRFFluorescenceMapping2 = relationship(
        "XRFFluorescenceMapping",
        primaryjoin="XFEFluorescenceComposite.r == XRFFluorescenceMapping.xrfFluorescenceMappingId",
    )


class ScreeningOutputLattice(Base):
    __tablename__ = "ScreeningOutputLattice"

    screeningOutputLatticeId = Column(INTEGER(10), primary_key=True)
    screeningOutputId = Column(
        ForeignKey(
            "ScreeningOutput.screeningOutputId", ondelete="CASCADE", onupdate="CASCADE"
        ),
        nullable=False,
        index=True,
        server_default=text("0"),
    )
    spaceGroup = Column(String(45))
    pointGroup = Column(String(45))
    bravaisLattice = Column(String(45))
    rawOrientationMatrix_a_x = Column(Float)
    rawOrientationMatrix_a_y = Column(Float)
    rawOrientationMatrix_a_z = Column(Float)
    rawOrientationMatrix_b_x = Column(Float)
    rawOrientationMatrix_b_y = Column(Float)
    rawOrientationMatrix_b_z = Column(Float)
    rawOrientationMatrix_c_x = Column(Float)
    rawOrientationMatrix_c_y = Column(Float)
    rawOrientationMatrix_c_z = Column(Float)
    unitCell_a = Column(Float)
    unitCell_b = Column(Float)
    unitCell_c = Column(Float)
    unitCell_alpha = Column(Float)
    unitCell_beta = Column(Float)
    unitCell_gamma = Column(Float)
    bltimeStamp = Column(
        TIMESTAMP,
        nullable=False,
        server_default=text("current_timestamp() ON UPDATE current_timestamp()"),
    )
    labelitIndexing = Column(TINYINT(1), server_default=text("0"))

    ScreeningOutput = relationship("ScreeningOutput")


class ScreeningStrategy(Base):
    __tablename__ = "ScreeningStrategy"

    screeningStrategyId = Column(INTEGER(10), primary_key=True)
    screeningOutputId = Column(
        ForeignKey(
            "ScreeningOutput.screeningOutputId", ondelete="CASCADE", onupdate="CASCADE"
        ),
        nullable=False,
        index=True,
        server_default=text("0"),
    )
    phiStart = Column(Float)
    phiEnd = Column(Float)
    rotation = Column(Float)
    exposureTime = Column(Float)
    resolution = Column(Float)
    completeness = Column(Float)
    multiplicity = Column(Float)
    anomalous = Column(TINYINT(1), nullable=False, server_default=text("0"))
    program = Column(String(45))
    rankingResolution = Column(Float)
    transmission = Column(
        Float, comment="Transmission for the strategy as given by the strategy program."
    )

    ScreeningOutput = relationship("ScreeningOutput")


class ScreeningStrategyWedge(Base):
    __tablename__ = "ScreeningStrategyWedge"

    screeningStrategyWedgeId = Column(
        INTEGER(10), primary_key=True, comment="Primary key"
    )
    screeningStrategyId = Column(
        ForeignKey(
            "ScreeningStrategy.screeningStrategyId",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        index=True,
        comment="Foreign key to parent table",
    )
    wedgeNumber = Column(
        INTEGER(10), comment="The number of this wedge within the strategy"
    )
    resolution = Column(Float)
    completeness = Column(Float)
    multiplicity = Column(Float)
    doseTotal = Column(Float, comment="Total dose for this wedge")
    numberOfImages = Column(INTEGER(10), comment="Number of images for this wedge")
    phi = Column(Float)
    kappa = Column(Float)
    chi = Column(Float)
    comments = Column(String(255))
    wavelength = Column(Float(asdecimal=True))

    ScreeningStrategy = relationship("ScreeningStrategy")


class ScreeningStrategySubWedge(Base):
    __tablename__ = "ScreeningStrategySubWedge"

    screeningStrategySubWedgeId = Column(
        INTEGER(10), primary_key=True, comment="Primary key"
    )
    screeningStrategyWedgeId = Column(
        ForeignKey(
            "ScreeningStrategyWedge.screeningStrategyWedgeId",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        index=True,
        comment="Foreign key to parent table",
    )
    subWedgeNumber = Column(
        INTEGER(10), comment="The number of this subwedge within the wedge"
    )
    rotationAxis = Column(String(45), comment="Angle where subwedge starts")
    axisStart = Column(Float, comment="Angle where subwedge ends")
    axisEnd = Column(Float, comment="Exposure time for subwedge")
    exposureTime = Column(Float, comment="Transmission for subwedge")
    transmission = Column(Float)
    oscillationRange = Column(Float)
    completeness = Column(Float)
    multiplicity = Column(Float)
    RESOLUTION = Column(Float)
    doseTotal = Column(Float, comment="Total dose for this subwedge")
    numberOfImages = Column(INTEGER(10), comment="Number of images for this subwedge")
    comments = Column(String(255))

    ScreeningStrategyWedge = relationship("ScreeningStrategyWedge")
