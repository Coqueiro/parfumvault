<?php 

require('../inc/sec.php');

require_once(__ROOT__.'/inc/config.php');
require_once(__ROOT__.'/inc/opendb.php');

if(!$_GET['fid']){
	echo '<div class="alert alert-danger"><strong>Error: </strong>no formula provided.</div>';
	return;
}

if(!mysqli_num_rows(mysqli_query($conn,"SELECT revisionDate FROM formulasRevisions WHERE fid = '".$_GET['fid']."'"))){
	echo '<div class="alert alert-info"><strong>No revisions available yet.</strong></div>';
	return;
}
$current_rev = mysqli_fetch_array(mysqli_query($conn, "SELECT revision FROM formulasMetaData WHERE fid = '".$_GET['fid']."'"));
$rev_q = mysqli_query($conn,"SELECT revision,revisionDate FROM formulasRevisions WHERE fid = '".$_GET['fid']."' GROUP BY revision");


?>
<table class="table table-bordered" width="100%" cellspacing="0">
	<thead>
     <tr class="noBorder">
      <th colspan="3">
       <div class="col-sm-6 text-left">
      <tr>
    <th width="33%" scope="col" align="center">Revision ID</th>
    <th width="33%" scope="col" align="center">Revision taken</th>
    <th width="33%" scope="col" align="center">Actions</th>
  </tr>
  </thead>
  <?php while ($rev = mysqli_fetch_array($rev_q)){ ?>
  <tr>
    <td align="center"><?=$rev['revision']?></td>
    <td align="center"><?=$rev['revisionDate']?></td>
    <td align="center"><?php if($rev['revision'] == $current_rev['revision']){ ?><strong>Current revision</strong><?php }else{ ?><a href="javascript:restoreRevision('<?=$rev['revision']?>')" class="fas fa-history" onclick="return confirm('Restore revision takken on <?=$rev['revisionDate']?> ?\nPlease note, this will overwrite the current formula.')"></a><?php } ?></td>
  </tr>
  <?php } ?>
</table>
</div>
