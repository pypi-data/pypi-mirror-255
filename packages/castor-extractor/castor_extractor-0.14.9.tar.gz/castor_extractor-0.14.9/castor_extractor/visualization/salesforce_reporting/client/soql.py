from ..assets import SalesforceReportingAsset

queries = {
    SalesforceReportingAsset.DASHBOARDS: """
        SELECT
            CreatedBy.Id,
            CreatedDate,
            Description,
            DeveloperName,
            FolderId,
            FolderName,
            Id,
            IsDeleted,
            LastReferencedDate,
            LastViewedDate,
            NamespacePrefix,
            RunningUserId,
            Title,
            Type
        FROM Dashboard
        WHERE IsDeleted = FALSE
    """,
    SalesforceReportingAsset.REPORTS: """
        SELECT
            CreatedBy.Id,
            Description,
            DeveloperName,
            FolderName,
            Format,
            Id,
            IsDeleted,
            LastReferencedDate,
            LastRunDate,
            LastViewedDate,
            Name,
            NamespacePrefix,
            OwnerId
        FROM Report
        WHERE IsDeleted = FALSE
    """,
    SalesforceReportingAsset.USERS: """
        SELECT
            Id,
            Email,
            FirstName,
            LastName,
            CreatedDate
        FROM User
    """,
}
