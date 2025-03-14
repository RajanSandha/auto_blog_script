# Ad Configuration Guide

This guide explains how to configure advertisements for your auto-generated blog.

## Environment Variables

Configure your ads by setting the following environment variables in your `.env` file:

```
# Ad Configuration
ADS_ENABLED=true                              # Enable/disable ads globally
ADS_GOOGLE_PUBLISHER_ID=pub-XXXXXXXXXXXXXXXX  # Google AdSense Publisher ID
ADS_GOOGLE_SIDEBAR_SLOT=XXXXXXXXXX            # Google AdSense Ad slot for sidebar
ADS_GOOGLE_CONTENT_SLOT=XXXXXXXXXX            # Google AdSense Ad slot for content
ADS_AMAZON_TRACKING_ID=XXXX-XX                # Amazon Associates tracking ID
ADS_CUSTOM_AD_CODE=<div>Your custom ad HTML</div>  # Custom HTML ad code
```

## How Auto-Blog Passes Environment Variables to Jekyll

Auto-Blog automatically creates a `_data/env.yml` file in your Jekyll site with all the ad configuration variables. This makes the environment variables accessible in your Jekyll templates without exposing sensitive information in your repository.

For example, you can access these variables in any Jekyll template like this:
```
{% if site.data.env.ads_enabled %}
  <!-- Ad code here -->
{% endif %}
```

## Available Ad Variables in Jekyll

The following variables are available in your Jekyll templates:

| Jekyll Variable | Environment Variable | Description |
|-----------------|----------------------|-------------|
| `site.data.env.ads_enabled` | `ADS_ENABLED` | Boolean flag to enable/disable ads |
| `site.data.env.google_publisher_id` | `ADS_GOOGLE_PUBLISHER_ID` | Google AdSense Publisher ID |
| `site.data.env.google_sidebar_slot` | `ADS_GOOGLE_SIDEBAR_SLOT` | Google AdSense Ad slot for sidebar |
| `site.data.env.google_content_slot` | `ADS_GOOGLE_CONTENT_SLOT` | Google AdSense Ad slot for content |
| `site.data.env.amazon_tracking_id` | `ADS_AMAZON_TRACKING_ID` | Amazon Associates tracking ID |
| `site.data.env.custom_ad_code` | `ADS_CUSTOM_AD_CODE` | Custom HTML ad code |

## Ad Placement

Auto-Blog includes these advertisements in the following locations:

1. **Sidebar**: Ad appears in the sidebar (if your theme supports it)
2. **In-content**: Ad appears after the introduction paragraph of each post (configurable)

## Custom Ad Placement

You can add ads to additional locations in your Jekyll template by using the environment variables:

```liquid
{% if site.data.env.ads_enabled %}
  <div class="custom-ad-location">
    {% if site.data.env.google_publisher_id %}
      <!-- Google AdSense code here -->
    {% elsif site.data.env.amazon_tracking_id %}
      <!-- Amazon Associates code here -->
    {% elsif site.data.env.custom_ad_code %}
      {{ site.data.env.custom_ad_code }}
    {% endif %}
  </div>
{% endif %}
```

## CSS Styling

Auto-Blog includes CSS styles for the advertisements in the `assets/css/custom.css` file. You can customize these styles by editing this file.

## Ad Blockers

Note that your readers may be using ad blockers. Consider providing alternative monetization methods or ensuring your content is valuable without ads.

## Compliance

Ensure your ads comply with:
1. Google AdSense policies
2. Amazon Associates policies 
3. GDPR and other privacy regulations
4. Your blog's audience expectations

Always include appropriate privacy policies when using advertisements.

## Troubleshooting

### Ads Not Appearing

1. Check that `ADS_ENABLED` is set to `true`
2. Verify your ad provider credentials
3. Check your web browser's console for errors
4. Disable ad blockers when testing

### Google AdSense Pending Review

Google AdSense may not show ads until your site is approved. During this time, placeholders may appear.

### Amazon Associates Not Working

Ensure you've been approved for the Amazon Associates program and verify your tracking ID is correct.

### Custom Ad Code Issues

If using custom ad HTML:
1. Ensure it's valid HTML
2. Check that it doesn't contain syntax that conflicts with Jekyll's Liquid template tags
3. Consider escaping special characters 