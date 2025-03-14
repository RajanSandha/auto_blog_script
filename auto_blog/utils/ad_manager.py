"""
Ad Manager for handling advertisement integration in blog posts.
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class AdManager:
    """
    Manages advertisements for blog posts.
    """
    
    def __init__(self, ads_config: Dict[str, Any]):
        """
        Initialize the ad manager with configuration.
        
        Args:
            ads_config: Dictionary containing ad configuration
        """
        self.enabled = ads_config.get('ads_enabled', False)
        self.position = ads_config.get('ads_position', 'sidebar')
        self.providers = ads_config.get('ads_providers', {})
        logger.info(f"Ad Manager initialized with enabled={self.enabled}, position={self.position}")
        
        if self.enabled:
            logger.info(f"Available ad providers: {list(self.providers.keys())}")
    
    def get_ad_code(self, provider_name: Optional[str] = None) -> str:
        """
        Get the HTML code for the specified ad provider.
        If no provider is specified, returns code for the first available provider.
        
        Args:
            provider_name: Name of the ad provider to use
            
        Returns:
            HTML code for the ad
        """
        if not self.enabled or not self.providers:
            return ""
        
        # If no provider specified, use the first available one
        if provider_name is None and self.providers:
            provider_name = next(iter(self.providers))
        
        # If the specified provider doesn't exist, return empty string
        if provider_name not in self.providers:
            logger.warning(f"Ad provider '{provider_name}' not found in configuration")
            return ""
        
        provider_config = self.providers[provider_name]
        
        # Generate the ad code based on the provider
        if provider_name.upper() == 'GOOGLE':
            return self._get_google_adsense_code(provider_config)
        elif provider_name.upper() == 'AMAZON':
            return self._get_amazon_ads_code(provider_config)
        elif provider_name.upper() == 'CUSTOM':
            return provider_config.get('HTML', '')
        else:
            # Generic ad code using the provider's HTML setting
            return provider_config.get('HTML', '')
    
    def _get_google_adsense_code(self, config: Dict[str, str]) -> str:
        """
        Generate Google AdSense code from the configuration.
        
        Args:
            config: Google AdSense specific configuration
            
        Returns:
            Google AdSense HTML code
        """
        publisher_id = config.get('PUBLISHER_ID', '')
        ad_slot = config.get('AD_SLOT', '')
        ad_format = config.get('FORMAT', 'auto')
        
        if not publisher_id or not ad_slot:
            logger.warning("Missing required Google AdSense configuration (PUBLISHER_ID or AD_SLOT)")
            return ""
        
        # Responsive ad code (best for sidebar)
        if self.position == 'sidebar':
            return f"""
<div class="ads-container">
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js"></script>
    <ins class="adsbygoogle"
         style="display:block"
         data-ad-client="ca-{publisher_id}"
         data-ad-slot="{ad_slot}"
         data-ad-format="{ad_format}"></ins>
    <script>
         (adsbygoogle = window.adsbygoogle || []).push({{}});
    </script>
</div>
"""
        else:
            # In-article ad code
            return f"""
<div class="ads-container ads-{self.position}">
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js"></script>
    <ins class="adsbygoogle"
         style="display:block; text-align:center;"
         data-ad-layout="in-article"
         data-ad-format="fluid"
         data-ad-client="ca-{publisher_id}"
         data-ad-slot="{ad_slot}"></ins>
    <script>
         (adsbygoogle = window.adsbygoogle || []).push({{}});
    </script>
</div>
"""
    
    def _get_amazon_ads_code(self, config: Dict[str, str]) -> str:
        """
        Generate Amazon Associates ad code from the configuration.
        
        Args:
            config: Amazon Associates specific configuration
            
        Returns:
            Amazon Associates HTML code
        """
        tracking_id = config.get('TRACKING_ID', '')
        marketplace = config.get('MARKETPLACE', 'US')
        ad_type = config.get('AD_TYPE', 'banner')
        
        if not tracking_id:
            logger.warning("Missing required Amazon Associates configuration (TRACKING_ID)")
            return ""
        
        # Different ad formats for different positions
        if ad_type == 'banner':
            return f"""
<div class="ads-container">
    <script type="text/javascript">
    amzn_assoc_ad_type = "banner";
    amzn_assoc_marketplace = "{marketplace}";
    amzn_assoc_region = "{marketplace.lower()}";
    amzn_assoc_placement = "";
    amzn_assoc_tracking_id = "{tracking_id}";
    amzn_assoc_linkid = "";
    </script>
    <script src="//z-na.amazon-adsystem.com/widgets/q?ServiceVersion=20070822&Operation=GetScript&ID=OneJS&WS=1"></script>
</div>
"""
        else:
            return f"""
<div class="ads-container">
    <script type="text/javascript">
    amzn_assoc_ad_type = "responsive_search_widget";
    amzn_assoc_tracking_id = "{tracking_id}";
    amzn_assoc_marketplace = "{marketplace}";
    amzn_assoc_region = "{marketplace.lower()}";
    amzn_assoc_placement = "";
    amzn_assoc_search_bar = "true";
    amzn_assoc_search_bar_position = "bottom";
    amzn_assoc_default_search_phrase = "";
    amzn_assoc_default_category = "All";
    amzn_assoc_linkid = "";
    amzn_assoc_title = "Shop Related Products";
    amzn_assoc_default_browse_node = "";
    amzn_assoc_rows = "1";
    </script>
    <script src="//z-na.amazon-adsystem.com/widgets/q?ServiceVersion=20070822&Operation=GetScript&ID=OneJS&WS=1&MarketPlace={marketplace}"></script>
</div>
"""
    
    def insert_ad_into_content(self, content: str) -> str:
        """
        Insert ad code into content based on the configured position.
        
        Args:
            content: The post content
            
        Returns:
            Content with ad code inserted
        """
        if not self.enabled or not self.providers:
            return content
        
        ad_code = self.get_ad_code()
        if not ad_code:
            return content
        
        # Insert ad based on position configuration
        if self.position == 'content_top':
            return f"{ad_code}\n\n{content}"
        elif self.position == 'content_bottom':
            return f"{content}\n\n{ad_code}"
        elif self.position == 'after_paragraph':
            # Insert after the first paragraph
            paragraphs = content.split('\n\n')
            if len(paragraphs) > 1:
                paragraphs.insert(1, ad_code)
                return '\n\n'.join(paragraphs)
            else:
                return f"{content}\n\n{ad_code}"
        else:
            # For 'sidebar' or any other position, we don't modify the content
            # The ad will be displayed in the sidebar via the theme's layout
            return content 