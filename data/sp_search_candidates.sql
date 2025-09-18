CREATE OR ALTER PROCEDURE dbo.sp_search_candidates
  @Q           NVARCHAR(100) = NULL,
  @Gender      NVARCHAR(16)  = NULL,
  @AgeMin      INT           = NULL,
  @AgeMax      INT           = NULL,
  @DistanceKm  INT           = NULL,
  @MyLat       FLOAT         = NULL,
  @MyLng       FLOAT         = NULL,
  @Element     NVARCHAR(32)  = NULL,
  @CungPhi     NVARCHAR(32)  = NULL,
  @Job         NVARCHAR(64)  = NULL,
  @FinanceMin  INT           = NULL,
  @FinanceMax  INT           = NULL,
  @Limit       INT           = 50,
  @Offset      INT           = 0
AS
BEGIN
  SET NOCOUNT ON;

  ;WITH base AS (
    SELECT
      cb.UserId,
      cb.FullName,
      cb.Gender,
      cb.Age,
      cb.Occupation,
      cb.FinanceMonthly,
      cb.ElementName,
      cb.CungPhiName,
      cb.AvatarUrl,
      cb.Latitude,
      cb.Longitude,
      CASE 
        WHEN @MyLat IS NOT NULL AND @MyLng IS NOT NULL AND cb.Latitude IS NOT NULL AND cb.Longitude IS NOT NULL
        THEN
          6371.0 * 2 * ASIN(SQRT(
            POWER(SIN(RADIANS(cb.Latitude - @MyLat)/2),2) +
            COS(RADIANS(@MyLat))*COS(RADIANS(cb.Latitude)) *
            POWER(SIN(RADIANS(cb.Longitude - @MyLng)/2),2)
          ))
        ELSE NULL
      END AS DistanceKm
    FROM dbo.vw_candidate_base cb
  )
  SELECT
    UserId,
    FullName,
    Gender,
    Age,
    Occupation,
    FinanceMonthly,
    ElementName,
    CungPhiName,
    AvatarUrl,
    DistanceKm
  FROM base
  WHERE (@Q IS NULL OR (FullName LIKE N'%' + @Q + N'%' OR Occupation LIKE N'%' + @Q + N'%'))
    AND (@Gender   IS NULL OR Gender = @Gender)
    AND (@AgeMin   IS NULL OR Age >= @AgeMin)
    AND (@AgeMax   IS NULL OR Age <= @AgeMax)
    AND (@Job      IS NULL OR Occupation LIKE N'%' + @Job + N'%')
    AND (@Element  IS NULL OR ElementName = @Element)
    AND (@CungPhi  IS NULL OR CungPhiName = @CungPhi)
    AND (@FinanceMin IS NULL OR FinanceMonthly IS NULL OR FinanceMonthly >= @FinanceMin)
    AND (@FinanceMax IS NULL OR FinanceMonthly IS NULL OR FinanceMonthly <= @FinanceMax)
    AND (@DistanceKm IS NULL OR (DistanceKm IS NOT NULL AND DistanceKm <= @DistanceKm))
  ORDER BY
    CASE WHEN DistanceKm IS NULL THEN 1 ELSE 0 END,
    DistanceKm,
    Age,
    FullName
  OFFSET @Offset ROWS
  FETCH NEXT @Limit ROWS ONLY;
END;
GO
